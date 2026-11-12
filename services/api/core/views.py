
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Business, BusinessMembership, Shop, Product, ProductCategory, StockBalance
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
