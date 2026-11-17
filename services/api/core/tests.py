
from decimal import Decimal
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import (
    Branch,
    Business,
    BusinessCurrency,
    BusinessGroup,
    BusinessMembership,
    BusinessRole,
    Compartment,
    ExchangeRate,
    GroupBusinessLink,
    GroupMembership,
    LegalEntity,
    MembershipRole,
    Product,
    ProductCategory,
    ProductPrice,
    Shop,
    ShopArea,
    ShopProductPrice,
    StockAllocation,
    StockBalance,
    Customer, Sale, SaleItem, Payment, CustomerLedgerEntry, StockMovement, AuditLog,
)
from .services import confirm_sale


User = get_user_model()


class BusinessFoundationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="group_owner",
            password="test-password",
        )
        self.employee = User.objects.create_user(
            username="employee",
            password="test-password",
        )

        self.business_a = Business.objects.create(
            name="Karibu Boutique",
            code="karibu-boutique",
        )
        self.business_b = Business.objects.create(
            name="Second Boutique",
            code="second-boutique",
        )

        self.group = BusinessGroup.objects.create(
            name="Example Business Group",
            code="example-group",
            created_by=self.owner,
        )

    def test_business_can_exist_independently(self):
        """A business does not have to belong to a group."""

        self.assertFalse(hasattr(self.business_a, "group_link"))

    def test_business_can_join_a_group_with_reporting_permissions(self):
        """Group reporting permissions can be configured."""

        link = GroupBusinessLink.objects.create(
            group=self.group,
            business=self.business_a,
            reporting_enabled=True,
            can_view_summary=True,
            can_view_financials=False,
        )

        self.assertEqual(link.group, self.group)
        self.assertTrue(link.can_view_summary)
        self.assertFalse(link.can_view_financials)

    def test_group_owner_can_be_registered(self):
        """A group owner is represented by a group membership."""

        membership = GroupMembership.objects.create(
            group=self.group,
            user=self.owner,
            role=GroupMembership.Role.OWNER,
        )

        self.assertEqual(membership.role, "OWNER")

    def test_business_role_cannot_be_assigned_across_businesses(self):
        """A membership cannot receive another business's role."""

        membership = BusinessMembership.objects.create(
            business=self.business_a,
            user=self.employee,
            status=BusinessMembership.Status.ACTIVE,
        )

        foreign_role = BusinessRole.objects.create(
            business=self.business_b,
            name="Manager",
            code="manager",
        )

        assignment = MembershipRole(
            membership=membership,
            role=foreign_role,
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()


class CatalogueAndInventoryTests(TestCase):
    def setUp(self):
        self.business = Business.objects.create(
            name="Test Retail Business",
            code="test-retail-business",
        )

        self.entity = LegalEntity.objects.create(
            business=self.business,
            legal_name="Test Retail Business Ltd",
        )

        self.branch = Branch.objects.create(
            legal_entity=self.entity,
            name="Kigali Branch",
            code="kigali",
        )

        self.shop = Shop.objects.create(
            branch=self.branch,
            name="Main Shop",
            code="main-shop",
        )

        self.currency = BusinessCurrency.objects.create(
            business=self.business,
            currency_code="RWF",
            is_default=True,
        )

        self.category = ProductCategory.objects.create(
            business=self.business,
            name="Beverages",
            code="beverages",
        )

        self.product = Product.objects.create(
            business=self.business,
            category=self.category,
            name="Mineral Water",
            sku="WATER-001",
        )

    def test_business_can_enable_multiple_currencies(self):
        """A business can use more than one currency."""

        usd = BusinessCurrency.objects.create(
            business=self.business,
            currency_code="USD",
        )

        self.assertEqual(self.business.currencies.count(), 2)
        self.assertEqual(usd.currency_code, "USD")

    def test_exchange_rate_rejects_foreign_business_currency(self):
        """An exchange rate cannot mix currencies from different businesses."""

        another_business = Business.objects.create(
            name="Another Business",
            code="another-business",
        )

        foreign_currency = BusinessCurrency.objects.create(
            business=another_business,
            currency_code="USD",
        )

        exchange_rate = ExchangeRate(
            business=self.business,
            from_currency=self.currency,
            to_currency=foreign_currency,
            rate="0.00070000",
            effective_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            exchange_rate.full_clean()

    def test_business_default_product_price(self):
        """A product can have a default selling price."""

        price = ProductPrice.objects.create(
            product=self.product,
            currency=self.currency,
            amount="1000.00",
            effective_from=timezone.now(),
        )

        self.assertEqual(Decimal(str(price.amount)), Decimal("1000.00"))

    def test_shop_can_override_business_product_price(self):
        """A shop can have a different selling price."""

        override = ShopProductPrice.objects.create(
            shop=self.shop,
            product=self.product,
            currency=self.currency,
            amount="1200.00",
            effective_from=timezone.now(),
        )

        self.assertEqual(Decimal(str(override.amount)), Decimal("1200.00"))

    def test_product_cannot_use_another_business_currency(self):
        """A product price must use its own business's currency."""

        another_business = Business.objects.create(
            name="Foreign Business",
            code="foreign-business",
        )

        foreign_currency = BusinessCurrency.objects.create(
            business=another_business,
            currency_code="USD",
        )

        price = ProductPrice(
            product=self.product,
            currency=foreign_currency,
            amount="10.00",
            effective_from=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            price.full_clean()

    def test_stock_can_be_allocated_to_a_shop_compartment(self):
        """Stock can be associated with a physical storage location."""

        area = ShopArea.objects.create(
            shop=self.shop,
            name="Left Shelf",
            code="left-shelf",
        )

        compartment = Compartment.objects.create(
            area=area,
            name="Shelf A01",
            code="A01",
        )

        balance = StockBalance.objects.create(
            shop=self.shop,
            product=self.product,
            quantity="50.000",
        )

        allocation = StockAllocation.objects.create(
            stock_balance=balance,
            compartment=compartment,
            quantity="20.000",
        )

        self.assertEqual(Decimal(str(allocation.quantity)), Decimal("20.000"))
        self.assertEqual(Decimal(str(balance.quantity)), Decimal("50.000"))

    def test_stock_cannot_be_allocated_to_another_shop(self):
        """A shop cannot allocate stock to another shop's compartment."""

        another_shop = Shop.objects.create(
            branch=self.branch,
            name="Second Shop",
            code="second-shop",
        )

        area = ShopArea.objects.create(
            shop=another_shop,
            name="Counter",
            code="counter",
        )

        compartment = Compartment.objects.create(
            area=area,
            name="Counter A01",
            code="counter-a01",
        )

        balance = StockBalance.objects.create(
            shop=self.shop,
            product=self.product,
            quantity="10.000",
        )

        allocation = StockAllocation(
            stock_balance=balance,
            compartment=compartment,
            quantity="5.000",
        )

        with self.assertRaises(ValidationError):
            allocation.full_clean()


class SaleTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", password="test-password")
        self.business = Business.objects.create(name="Sales Test Business", code="sales-test-business")
        self.entity = LegalEntity.objects.create(business=self.business, legal_name="Sales Test Ltd")
        self.branch = Branch.objects.create(legal_entity=self.entity, name="Main", code="main")
        self.shop = Shop.objects.create(branch=self.branch, name="Main Shop", code="main-shop")
        self.membership = BusinessMembership.objects.create(
            business=self.business, user=self.user, status=BusinessMembership.Status.ACTIVE,
        )
        self.currency = BusinessCurrency.objects.create(
            business=self.business, currency_code="RWF", is_default=True,
        )
        self.product = Product.objects.create(
            business=self.business, name="Test Shirt", sku="SHIRT-001", track_stock=True,
        )
        ProductPrice.objects.create(
            product=self.product, currency=self.currency, amount="5000.00",
            effective_from=timezone.now() - timedelta(days=1),
        )
        self.stock = StockBalance.objects.create(
            shop=self.shop, product=self.product, quantity="10.000",
        )
        self.customer = Customer.objects.create(
            business=self.business, name="Test Customer", phone="0780000000",
            credit_limit="20000.00",
        )

    def _sale(self, **overrides):
        from uuid import uuid4
        payload = {
            "user": self.user, "business_id": self.business.id,
            "shop_id": self.shop.id, "currency_code": "RWF",
            "idempotency_key": uuid4(),
            "items": [{"product_id": self.product.id, "quantity": "2.000"}],
            "payments": [{"method": "CASH", "amount": "5000.00"}],
            "customer_id": self.customer.id,
        }
        payload.update(overrides)
        return confirm_sale(**payload)

    def test_sale_creates_linked_records_and_deducts_stock(self):
        sale, created = self._sale()
        self.assertTrue(created)
        self.assertEqual(sale.total, Decimal("10000.00"))
        self.assertEqual(sale.balance_due, Decimal("5000.00"))
        self.assertEqual(self.stock.__class__.objects.get(pk=self.stock.pk).quantity, Decimal("8.000"))
        self.assertEqual(SaleItem.objects.filter(sale=sale).count(), 1)
        self.assertEqual(Payment.objects.filter(sale=sale).count(), 1)
        self.assertEqual(CustomerLedgerEntry.objects.filter(sale=sale).count(), 1)
        self.assertEqual(StockMovement.objects.filter(sale=sale).count(), 1)
        self.assertEqual(AuditLog.objects.filter(object_id=str(sale.id)).count(), 1)

    def test_insufficient_stock_creates_no_sale(self):
        from rest_framework.exceptions import ValidationError as APIValidationError
        with self.assertRaises(APIValidationError):
            self._sale(items=[{"product_id": self.product.id, "quantity": "99.000"}])
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(self.stock.__class__.objects.get(pk=self.stock.pk).quantity, Decimal("10.000"))

    def test_mobile_money_reference_is_pending_not_settled(self):
        sale, _ = self._sale(
            payments=[{"method": "MOBILE_MONEY", "amount": "10000.00", "reference": "MM-REF-1"}],
        )
        payment = Payment.objects.get(sale=sale)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(sale.amount_paid, Decimal("0.00"))
        self.assertEqual(sale.pending_payment_total, Decimal("10000.00"))
        self.assertEqual(sale.balance_due, Decimal("0.00"))

    def test_same_idempotency_key_does_not_create_duplicate_sale(self):
        from uuid import uuid4
        key = uuid4()
        first, created_first = self._sale(idempotency_key=key)
        second, created_second = self._sale(idempotency_key=key)
        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first.id, second.id)
        self.assertEqual(Sale.objects.count(), 1)

    def test_idempotency_key_collision_never_returns_another_business_sale(self):
        from uuid import uuid4
        from rest_framework.exceptions import ValidationError as APIValidationError

        foreign_user = User.objects.create_user(username="foreign-seller", password="test-password")
        foreign_business = Business.objects.create(name="Foreign Business", code="foreign-business")
        foreign_entity = LegalEntity.objects.create(business=foreign_business, legal_name="Foreign Ltd")
        foreign_branch = Branch.objects.create(legal_entity=foreign_entity, name="Foreign Branch", code="foreign")
        foreign_shop = Shop.objects.create(branch=foreign_branch, name="Foreign Shop", code="foreign-shop")
        foreign_currency = BusinessCurrency.objects.create(
            business=foreign_business, currency_code="RWF", is_default=True,
        )
        key = uuid4()
        foreign_sale = Sale.objects.create(
            business=foreign_business,
            shop=foreign_shop,
            created_by=foreign_user,
            receipt_number="FOREIGN-RECEIPT-001",
            idempotency_key=key,
            currency=foreign_currency,
            subtotal="100.00",
            total="100.00",
            amount_paid="100.00",
            pending_payment_total="0.00",
            balance_due="0.00",
            confirmed_at=timezone.now(),
        )

        with self.assertRaises(APIValidationError):
            self._sale(idempotency_key=key)

        self.assertEqual(Sale.objects.count(), 1)
        self.assertTrue(Sale.objects.filter(pk=foreign_sale.pk, business=foreign_business).exists())
