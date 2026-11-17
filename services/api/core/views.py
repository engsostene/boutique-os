
from decimal import Decimal

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from .models import Business, BusinessMembership, Shop, Product, ProductCategory, StockBalance
from .services import confirm_sale
from .serializers import (
    BusinessSerializer,
    ShopSerializer,
    ProductSerializer,
    ProductCategorySerializer,
    StockBalanceSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "application": "Rwanda Boutique OS",
        "status": "operational",
        "message": "Backend API is responding successfully.",
    })


def get_accessible_business(user, business_id):
    membership = BusinessMembership.objects.filter(
        user=user,
        business_id=business_id,
        status=BusinessMembership.Status.ACTIVE,
    ).select_related("business").first()

    if not membership:
        return None

    return membership.business


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def business_list(request):
    businesses = Business.objects.filter(
        memberships__user=request.user,
        memberships__status=BusinessMembership.Status.ACTIVE,
    ).distinct()

    return Response(BusinessSerializer(businesses, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def shop_list(request, business_id):
    business = get_accessible_business(request.user, business_id)

    if not business:
        return Response(
            {"detail": "Business not found or access denied."},
            status=404,
        )

    shops = Shop.objects.filter(
        branch__legal_entity__business=business,
        is_active=True,
    ).select_related("branch")

    return Response(ShopSerializer(shops, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def category_list(request, business_id):
    business = get_accessible_business(request.user, business_id)

    if not business:
        return Response(
            {"detail": "Business not found or access denied."},
            status=404,
        )

    categories = ProductCategory.objects.filter(
        business=business,
    ).order_by("name")

    return Response(ProductCategorySerializer(categories, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_list(request, business_id):
    business = get_accessible_business(request.user, business_id)

    if not business:
        return Response(
            {"detail": "Business not found or access denied."},
            status=404,
        )

    shop = None
    shop_id = request.query_params.get("shop_id")

    if shop_id:
        shop = Shop.objects.filter(
            id=shop_id,
            branch__legal_entity__business=business,
            is_active=True,
        ).first()

        if not shop:
            return Response(
                {"detail": "Shop not found in this business."},
                status=404,
            )

    currency_code = request.query_params.get(
        "currency",
        business.default_currency,
    ).upper()

    products = Product.objects.filter(
        business=business,
        status=Product.Status.ACTIVE,
    ).select_related("category").prefetch_related("aliases").order_by("name")

    serializer = ProductSerializer(
        products,
        many=True,
        context={
            "shop": shop,
            "currency_code": currency_code,
        },
    )

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_list(request, business_id, shop_id):
    business = get_accessible_business(request.user, business_id)

    if not business:
        return Response(
            {"detail": "Business not found or access denied."},
            status=404,
        )

    shop = Shop.objects.filter(
        id=shop_id,
        branch__legal_entity__business=business,
    ).first()

    if not shop:
        return Response(
            {"detail": "Shop not found in this business."},
            status=404,
        )

    balances = StockBalance.objects.filter(
        shop=shop,
    ).select_related("product").prefetch_related(
        "allocations__compartment"
    ).order_by("product__name")

    return Response(StockBalanceSerializer(balances, many=True).data)


class SaleItemInputSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3, min_value=Decimal("0.001"))


class SalePaymentInputSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["CASH", "MOBILE_MONEY", "BANK"])
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.01"))
    reference = serializers.CharField(required=False, allow_blank=True, max_length=120)


class SaleConfirmationInputSerializer(serializers.Serializer):
    shop_id = serializers.UUIDField()
    currency = serializers.CharField(max_length=3)
    idempotency_key = serializers.UUIDField()
    customer_id = serializers.UUIDField(required=False, allow_null=True)
    items = SaleItemInputSerializer(many=True)
    payments = SalePaymentInputSerializer(many=True, required=False)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sale_confirm(request, business_id):
    """Validate the request shape, then delegate business rules to the atomic service."""
    serializer = SaleConfirmationInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    sale, created = confirm_sale(
        user=request.user, business_id=business_id,
        shop_id=data["shop_id"], currency_code=data["currency"],
        idempotency_key=data["idempotency_key"],
        customer_id=data.get("customer_id"),
        items=data["items"], payments=data.get("payments", []),
    )
    return Response({
        "id": str(sale.id), "receipt_number": sale.receipt_number,
        "status": sale.status, "currency": sale.currency.currency_code,
        "subtotal": str(sale.subtotal), "total": str(sale.total),
        "amount_paid": str(sale.amount_paid),
        "pending_payment_total": str(sale.pending_payment_total),
        "balance_due": str(sale.balance_due),
        "created": created,
    }, status=201 if created else 200)
