
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Business,
    BusinessCurrency,
    Product,
    ProductAlias,
    ProductCategory,
    Shop,
    Compartment,
    StockBalance,
    StockAllocation,
    ProductPrice,
    ShopProductPrice,
)


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["id", "name", "code", "default_currency", "timezone", "status"]


class ShopSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = Shop
        fields = ["id", "name", "code", "address", "branch_name", "is_active"]


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "code"]


class ProductAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAlias
        fields = ["alias", "language_code"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
        default=None,
    )
    aliases = ProductAliasSerializer(many=True, read_only=True)
    selling_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()

    def get_selling_price(self, product):
        shop = self.context.get("shop")
        currency_code = self.context.get("currency_code")
        now = timezone.now()

        if not currency_code:
            currency_code = product.business.default_currency

        currency = BusinessCurrency.objects.filter(
            business=product.business,
            currency_code=currency_code,
            is_active=True,
        ).first()

        if not currency:
            return None

        active_period = (
            Q(effective_to__isnull=True)
            | Q(effective_to__gt=now)
        )

        if shop:
            override = ShopProductPrice.objects.filter(
                shop=shop,
                product=product,
                currency=currency,
                effective_from__lte=now,
            ).filter(active_period).order_by("-effective_from").first()

            if override:
                return str(override.amount)

        default_price = ProductPrice.objects.filter(
            product=product,
            currency=currency,
            effective_from__lte=now,
        ).filter(active_period).order_by("-effective_from").first()

        return str(default_price.amount) if default_price else None

    def get_currency(self, product):
        return self.context.get("currency_code") or product.business.default_currency

    def get_stock_quantity(self, product):
        shop = self.context.get("shop")

        if not shop or not product.track_stock:
            return None

        balance = StockBalance.objects.filter(
            shop=shop,
            product=product,
        ).first()

        return str(balance.quantity) if balance else "0.000"

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "barcode",
            "description",
            "base_unit",
            "track_stock",
            "status",
            "category_name",
            "aliases",
            "selling_price",
            "currency",
            "stock_quantity",
        ]


class CompartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compartment
        fields = ["id", "name", "code", "description"]


class StockAllocationSerializer(serializers.ModelSerializer):
    compartment_name = serializers.CharField(
        source="compartment.name",
        read_only=True,
    )
    compartment_code = serializers.CharField(
        source="compartment.code",
        read_only=True,
    )

    class Meta:
        model = StockAllocation
        fields = ["id", "quantity", "compartment_name", "compartment_code"]


class StockBalanceSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )
    product_sku = serializers.CharField(
        source="product.sku",
        read_only=True,
    )
    allocations = StockAllocationSerializer(many=True, read_only=True)

    class Meta:
        model = StockBalance
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "reorder_level",
            "allocations",
        ]
