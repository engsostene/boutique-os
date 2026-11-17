"""Business operations that must preserve cross-model invariants."""
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    AuditLog, BusinessMembership, BusinessCurrency, Customer,
    CustomerLedgerEntry, Payment, Product, ProductPrice, Sale,
    SaleItem, Shop, ShopProductPrice, StockBalance, StockMovement,
)

CENT = Decimal("0.01")


def _money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


@transaction.atomic
def confirm_sale(*, user, business_id, shop_id, currency_code, idempotency_key,
                 items, payments, customer_id=None):
    """Confirm a sale atomically; never trust client-submitted prices or totals."""
    try:
        key = UUID(str(idempotency_key))
    except (TypeError, ValueError):
        raise ValidationError({"idempotency_key": "A valid UUID is required."})

    membership = BusinessMembership.objects.filter(
        business_id=business_id, user=user,
        status=BusinessMembership.Status.ACTIVE,
    ).exists()
    if not membership:
        raise ValidationError("You do not have access to this business.")

    existing = Sale.objects.filter(idempotency_key=key, business_id=business_id).first()
    if existing:
        if existing.created_by_id != user.id:
            raise ValidationError("This request key is already used.")
        return existing, False

    shop = Shop.objects.select_related("branch__legal_entity").filter(
        id=shop_id, branch__legal_entity__business_id=business_id, is_active=True,
    ).first()
    if not shop:
        raise ValidationError({"shop": "Shop is not active in this business."})

    currency = BusinessCurrency.objects.filter(
        business_id=business_id, currency_code=currency_code.upper(), is_active=True,
    ).first()
    if not currency:
        raise ValidationError({"currency": "Currency is not enabled for this business."})

    customer = None
    if customer_id:
        customer = Customer.objects.select_for_update().filter(
            id=customer_id, business_id=business_id, is_active=True,
        ).first()
        if not customer:
            raise ValidationError({"customer": "Customer is not active in this business."})

    if not items:
        raise ValidationError({"items": "A sale must contain at least one item."})

    now = timezone.now()
    active_period = Q(effective_to__isnull=True) | Q(effective_to__gt=now)
    prepared = []
    seen_products = set()
    subtotal = Decimal("0.00")
    locked_balances = {}

    # Lock stock rows before checking quantities to prevent concurrent overselling.
    for line in items:
        try:
            product_id = line["product_id"]
            quantity = Decimal(str(line["quantity"]))
        except (KeyError, TypeError, ValueError):
            raise ValidationError({"items": "Each item needs product_id and a valid quantity."})
        if not quantity.is_finite() or quantity <= 0:
            raise ValidationError({"items": "Quantities must be greater than zero."})

        if str(product_id) in seen_products:
            raise ValidationError({"items": "Include each product once and combine its quantities."})
        seen_products.add(str(product_id))

        product = Product.objects.filter(
            id=product_id, business_id=business_id, status=Product.Status.ACTIVE,
        ).first()
        if not product:
            raise ValidationError({"items": f"Product {product_id} is unavailable."})

        override = ShopProductPrice.objects.filter(
            shop=shop, product=product, currency=currency,
            effective_from__lte=now,
        ).filter(active_period).order_by("-effective_from").first()
        price = override or ProductPrice.objects.filter(
            product=product, currency=currency, effective_from__lte=now,
        ).filter(active_period).order_by("-effective_from").first()
        if not price:
            raise ValidationError({"items": f"No active {currency.currency_code} price for {product.name}."})

        balance = None
        if product.track_stock:
            balance = StockBalance.objects.select_for_update().filter(
                shop=shop, product=product,
            ).first()
            if not balance or balance.quantity < quantity:
                available = balance.quantity if balance else Decimal("0.000")
                raise ValidationError({"stock": f"Insufficient stock for {product.name}. Available: {available}."})
            locked_balances[product.id] = balance

        unit_price = _money(price.amount)
        line_total = _money(unit_price * quantity)
        subtotal += line_total
        prepared.append((product, quantity, unit_price, line_total, balance))

    subtotal = _money(subtotal)
    paid = Decimal("0.00")
    pending_total = Decimal("0.00")
    payment_rows = []
    for payment in payments:
        try:
            method = payment["method"]
            amount = _money(payment["amount"])
        except (KeyError, TypeError, ValueError):
            raise ValidationError({"payments": "Each payment needs a method and valid amount."})
        if method not in Payment.Method.values or amount <= 0:
            raise ValidationError({"payments": "Payment method or amount is invalid."})
        if method == Payment.Method.MOBILE_MONEY and not payment.get("reference"):
            raise ValidationError({"payments": "Mobile Money reference is required."})
        payment_rows.append((method, amount, str(payment.get("reference", ""))))
        if method == Payment.Method.MOBILE_MONEY:
            # A typed reference is not provider confirmation, so it is not cash received.
            pending_total += amount
        else:
            paid += amount

    paid = _money(paid)
    pending_total = _money(pending_total)
    if paid + pending_total > subtotal:
        raise ValidationError({"payments": "Payments cannot exceed the sale total."})
    # Pending Mobile Money is tracked separately from both settled money and customer credit.
    balance_due = _money(subtotal - paid - pending_total)
    if balance_due and not customer:
        raise ValidationError({"customer": "A customer is required when a sale has an outstanding balance."})

    if balance_due:
        # Existing ledger convention: positive entries increase the customer's debt.
        from django.db.models import Sum
        current_debt = CustomerLedgerEntry.objects.filter(
            customer=customer, currency=currency,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        if current_debt + balance_due > customer.credit_limit:
            raise ValidationError({"credit": "Customer credit limit would be exceeded."})

    receipt_number = f"S-{now:%Y%m%d}-{key.hex[:20].upper()}"
    try:
        # Inner savepoint lets us safely recover from a concurrent duplicate-key request.
        with transaction.atomic():
            sale = Sale.objects.create(
                business_id=business_id, shop=shop, customer=customer,
                created_by=user, receipt_number=receipt_number,
                idempotency_key=key, currency=currency,
                subtotal=subtotal, total=subtotal, amount_paid=paid,
                pending_payment_total=pending_total, balance_due=balance_due, confirmed_at=now,
            )
    except IntegrityError:
        # A concurrent retry may have won the unique idempotency key race.
        sale = Sale.objects.filter(
            idempotency_key=key,
            business_id=business_id,
        ).first()
        if sale is None:
            # The globally unique key belongs to another tenant. Never return
            # that tenant's object or disclose its existence through the API.
            raise ValidationError({
                "idempotency_key": "This request key cannot be used. Generate a new key and retry."
            })
        if sale.created_by_id != user.id:
            raise ValidationError({
                "idempotency_key": "This request key is already used. Generate a new key and retry."
            })
        return sale, False

    for product, quantity, unit_price, line_total, balance in prepared:
        SaleItem.objects.create(
            sale=sale, product=product, product_name=product.name,
            sku=product.sku, quantity=quantity,
            unit_price=unit_price, line_total=line_total,
        )
        if balance:
            balance.quantity -= quantity
            balance.save(update_fields=["quantity", "updated_at"])
            StockMovement.objects.create(
                shop=shop, product=product, sale=sale,
                movement_type=StockMovement.MovementType.SALE,
                quantity_delta=-quantity, balance_after=balance.quantity,
                note=f"Sale {receipt_number}", created_by=user,
            )

    for method, amount, reference in payment_rows:
        Payment.objects.create(
            sale=sale, method=method, amount=amount,
            status=(Payment.Status.PENDING if method == Payment.Method.MOBILE_MONEY else Payment.Status.RECORDED),
            reference=reference, received_at=now, recorded_by=user,
        )

    if balance_due:
        CustomerLedgerEntry.objects.create(
            customer=customer, sale=sale,
            entry_type=CustomerLedgerEntry.EntryType.SALE_CREDIT,
            currency=currency, amount=balance_due,
            description=f"Outstanding balance for {receipt_number}",
            created_by=user,
        )

    AuditLog.objects.create(
        business_id=business_id, actor=user, action="SALE_CONFIRMED",
        object_type="Sale", object_id=str(sale.id),
        summary=f"Sale {receipt_number} confirmed for {sale.total} {currency.currency_code}",
    )
    return sale, True
