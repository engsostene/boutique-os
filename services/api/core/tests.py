
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
)


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

        self.assertEqual(price.amount, 1000)

    def test_shop_can_override_business_product_price(self):
        """A shop can have a different selling price."""

        override = ShopProductPrice.objects.create(
            shop=self.shop,
            product=self.product,
            currency=self.currency,
            amount="1200.00",
            effective_from=timezone.now(),
        )

        self.assertEqual(override.amount, 1200)

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

        self.assertEqual(allocation.quantity, 20)
        self.assertEqual(balance.quantity, 50)

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
