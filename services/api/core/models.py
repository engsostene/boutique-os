
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


# ============================================================
# COMMON MODEL BASE
# ============================================================

class BaseModel(models.Model):
    """Shared UUID identifier and timestamps for business records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================
# BUSINESS GROUP AND GROUP MEMBERSHIP
# ============================================================

class BusinessGroup(BaseModel):
    """A group that can oversee multiple independent businesses."""

    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=60, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_business_groups",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class GroupMembership(BaseModel):
    """A user's role within a business group."""

    class Role(models.TextChoices):
        OWNER = "OWNER", "Group Owner"
        ADMIN = "ADMIN", "Group Administrator"
        VIEWER = "VIEWER", "Group Viewer"

    group = models.ForeignKey(
        BusinessGroup,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="group_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["group", "user"],
                name="unique_group_user_membership",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.group} ({self.role})"


# ============================================================
# BUSINESS
# ============================================================

class Business(BaseModel):
    """An independently managed business within the platform."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        SUSPENDED = "SUSPENDED", "Suspended"

    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=60, unique=True)
    default_currency = models.CharField(max_length=3, default="RWF")
    timezone = models.CharField(max_length=60, default="Africa/Kigali")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    def __str__(self):
        return self.name


class GroupBusinessLink(BaseModel):
    """Optional relationship between a business and a business group."""

    group = models.ForeignKey(
        BusinessGroup,
        on_delete=models.PROTECT,
        related_name="business_links",
    )
    business = models.OneToOneField(
        Business,
        on_delete=models.PROTECT,
        related_name="group_link",
    )
    reporting_enabled = models.BooleanField(default=True)
    can_view_summary = models.BooleanField(default=True)
    can_view_financials = models.BooleanField(default=False)
    can_view_operations = models.BooleanField(default=False)
    can_view_customer_details = models.BooleanField(default=False)
    can_approve_requests = models.BooleanField(default=False)

    def clean(self):
        if not self.reporting_enabled and any([
            self.can_view_summary,
            self.can_view_financials,
            self.can_view_operations,
            self.can_view_customer_details,
            self.can_approve_requests,
        ]):
            raise ValidationError(
                "Reporting permissions cannot be enabled when reporting is disabled."
            )

    def __str__(self):
        return f"{self.business} -> {self.group}"


# ============================================================
# LEGAL AND OPERATIONAL STRUCTURE
# ============================================================

class LegalEntity(BaseModel):
    """A legally recognized entity with its own accounting identity."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="legal_entities",
    )
    legal_name = models.CharField(max_length=180)
    registration_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    tax_identifier = models.CharField(max_length=100, blank=True)
    base_currency = models.CharField(max_length=3, default="RWF")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "registration_number"],
                condition=models.Q(registration_number__isnull=False),
                name="unique_legal_registration_per_business",
            )
        ]

    def __str__(self):
        return self.legal_name


class Branch(BaseModel):
    """An operational division of a legal entity."""

    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.PROTECT,
        related_name="branches",
    )
    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=60)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["legal_entity", "code"],
                name="unique_branch_code_per_entity",
            )
        ]

    def __str__(self):
        return self.name


class Shop(BaseModel):
    """A physical retail location belonging to a branch."""

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="shops",
    )
    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=60)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "code"],
                name="unique_shop_code_per_branch",
            )
        ]

    def __str__(self):
        return self.name


# ============================================================
# BUSINESS MEMBERSHIPS, ROLES AND PERMISSIONS
# ============================================================

class BusinessMembership(BaseModel):
    """Connects a platform user to a business they can access."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INVITED = "INVITED", "Invited"
        SUSPENDED = "SUSPENDED", "Suspended"
        REMOVED = "REMOVED", "Removed"

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="business_memberships",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INVITED,
    )
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "user"],
                name="unique_business_user_membership",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.business}"


class BusinessRole(BaseModel):
    """A business-specific role, including custom roles."""

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="roles",
    )
    name = models.CharField(max_length=80)
    code = models.SlugField(max_length=60)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "code"],
                name="unique_role_code_per_business",
            )
        ]

    def __str__(self):
        return f"{self.business}: {self.name}"


class Permission(BaseModel):
    """A reusable permission definition across the platform."""

    code = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)
    module = models.CharField(max_length=60)

    def __str__(self):
        return self.code


class RolePermission(BaseModel):
    """Permissions assigned to a business role."""

    role = models.ForeignKey(
        BusinessRole,
        on_delete=models.PROTECT,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.PROTECT,
        related_name="role_permissions",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_permission_per_role",
            )
        ]


class MembershipRole(BaseModel):
    """Assigns one or more business roles to a membership."""

    membership = models.ForeignKey(
        BusinessMembership,
        on_delete=models.PROTECT,
        related_name="assigned_roles",
    )
    role = models.ForeignKey(
        BusinessRole,
        on_delete=models.PROTECT,
        related_name="member_assignments",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["membership", "role"],
                name="unique_role_per_membership",
            )
        ]

    def clean(self):
        if (
            self.membership_id
            and self.role_id
            and self.membership.business_id != self.role.business_id
        ):
            raise ValidationError(
                "A user can only receive roles belonging to their business."
            )

    def __str__(self):
        return f"{self.membership} - {self.role}"


# ============================================================
# BUSINESS CURRENCIES AND EXCHANGE RATES
# ============================================================

class BusinessCurrency(BaseModel):
    """Currencies enabled for transactions within a business."""

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="currencies",
    )
    currency_code = models.CharField(max_length=3)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "currency_code"],
                name="unique_currency_per_business",
            )
        ]

    def clean(self):
        if self.currency_code:
            self.currency_code = self.currency_code.upper()

    def __str__(self):
        return f"{self.business} - {self.currency_code}"


class ExchangeRate(BaseModel):
    """A recorded exchange rate between two business currencies."""

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="exchange_rates",
    )
    from_currency = models.ForeignKey(
        BusinessCurrency,
        on_delete=models.PROTECT,
        related_name="rates_from",
    )
    to_currency = models.ForeignKey(
        BusinessCurrency,
        on_delete=models.PROTECT,
        related_name="rates_to",
    )
    rate = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(0.00000001)],
    )
    effective_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_currency", "to_currency", "effective_at"],
                name="unique_exchange_rate_at_time",
            )
        ]

    def clean(self):
        if self.from_currency_id and self.to_currency_id:
            if self.from_currency.business_id != self.business_id:
                raise ValidationError(
                    "Source currency belongs to another business."
                )
            if self.to_currency.business_id != self.business_id:
                raise ValidationError(
                    "Target currency belongs to another business."
                )
            if self.from_currency_id == self.to_currency_id:
                raise ValidationError(
                    "Source and target currencies must differ."
                )

    def __str__(self):
        return f"{self.from_currency} -> {self.to_currency}: {self.rate}"


# ============================================================
# PRODUCT CATALOGUE
# ============================================================

class ProductCategory(BaseModel):
    """A business-specific way of grouping products."""

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="product_categories",
    )
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=60)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "code"],
                name="unique_category_code_per_business",
            )
        ]

    def __str__(self):
        return self.name


class ProductFamily(BaseModel):
    """An optional parent grouping for related sellable products."""

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="product_families",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_product_family_per_business",
            )
        ]

    def __str__(self):
        return self.name


class Product(BaseModel):
    """A sellable product or variant in the shared business catalogue."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        DISCONTINUED = "DISCONTINUED", "Discontinued"

    business = models.ForeignKey(
        Business,
        on_delete=models.PROTECT,
        related_name="products",
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    family = models.ForeignKey(
        ProductFamily,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=180)
    sku = models.CharField(max_length=80)
    barcode = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    base_unit = models.CharField(max_length=30, default="piece")
    track_stock = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["business", "sku"],
                name="unique_product_sku_per_business",
            ),
            models.UniqueConstraint(
                fields=["business", "barcode"],
                condition=models.Q(barcode__isnull=False),
                name="unique_product_barcode_per_business",
            ),
        ]

    def clean(self):
        if self.category_id and self.category.business_id != self.business_id:
            raise ValidationError("Category belongs to another business.")
        if self.family_id and self.family.business_id != self.business_id:
            raise ValidationError("Product family belongs to another business.")

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductAlias(BaseModel):
    """Alternative names used by shopkeepers to find a product."""

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="aliases",
    )
    alias = models.CharField(max_length=150)
    language_code = models.CharField(max_length=10, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "alias"],
                name="unique_alias_per_product",
            )
        ]

    def __str__(self):
        return self.alias


# ============================================================
# BUSINESS DEFAULT PRICES AND SHOP PRICE OVERRIDES
# ============================================================

class ProductPrice(BaseModel):
    """A default selling price for a product in a business currency."""

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="default_prices",
    )
    currency = models.ForeignKey(
        BusinessCurrency,
        on_delete=models.PROTECT,
        related_name="product_prices",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "currency", "effective_from"],
                name="unique_product_price_start",
            )
        ]

    def clean(self):
        if self.product_id and self.currency_id:
            if self.product.business_id != self.currency.business_id:
                raise ValidationError(
                    "Price currency belongs to another business."
                )
        if self.effective_to and self.effective_to <= self.effective_from:
            raise ValidationError("Price end must be after its start.")


class ShopProductPrice(BaseModel):
    """An optional shop-specific override of the business default price."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        related_name="product_price_overrides",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="shop_price_overrides",
    )
    currency = models.ForeignKey(
        BusinessCurrency,
        on_delete=models.PROTECT,
        related_name="shop_prices",
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "product", "currency", "effective_from"],
                name="unique_shop_product_price_start",
            )
        ]

    def clean(self):
        if self.product_id and self.shop_id and self.currency_id:
            business_id = self.product.business_id
            shop_business_id = self.shop.branch.legal_entity.business_id

            if shop_business_id != business_id:
                raise ValidationError(
                    "Shop and product belong to different businesses."
                )
            if self.currency.business_id != business_id:
                raise ValidationError(
                    "Price currency belongs to another business."
                )

        if self.effective_to and self.effective_to <= self.effective_from:
            raise ValidationError("Price end must be after its start.")


# ============================================================
# PHYSICAL SHOP LAYOUT
# ============================================================

class ShopArea(BaseModel):
    """A named physical area inside a shop."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        related_name="areas",
    )
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=60)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "code"],
                name="unique_area_code_per_shop",
            )
        ]

    def __str__(self):
        return f"{self.shop} - {self.name}"


class Compartment(BaseModel):
    """A shelf, cupboard, counter section or other storage position."""

    area = models.ForeignKey(
        ShopArea,
        on_delete=models.PROTECT,
        related_name="compartments",
    )
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=60)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["area", "code"],
                name="unique_compartment_code_per_area",
            )
        ]

    def __str__(self):
        return f"{self.area} - {self.code}"


# ============================================================
# STOCK BALANCES AND PHYSICAL ALLOCATIONS
# ============================================================

class StockBalance(BaseModel):
    """The total recorded stock of one product at one shop."""

    shop = models.ForeignKey(
        Shop,
        on_delete=models.PROTECT,
        related_name="stock_balances",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="stock_balances",
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=0,
    )
    reorder_level = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shop", "product"],
                name="unique_product_stock_per_shop",
            )
        ]

    def clean(self):
        if self.shop_id and self.product_id:
            shop_business_id = self.shop.branch.legal_entity.business_id
            if shop_business_id != self.product.business_id:
                raise ValidationError(
                    "Shop and product belong to different businesses."
                )

    def __str__(self):
        return f"{self.product} at {self.shop}: {self.quantity}"


class StockAllocation(BaseModel):
    """The portion of a shop's stock held in a physical compartment."""

    stock_balance = models.ForeignKey(
        StockBalance,
        on_delete=models.PROTECT,
        related_name="allocations",
    )
    compartment = models.ForeignKey(
        Compartment,
        on_delete=models.PROTECT,
        related_name="stock_allocations",
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=3,
        default=0,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stock_balance", "compartment"],
                name="unique_stock_allocation_per_compartment",
            )
        ]

    def clean(self):
        if self.stock_balance_id and self.compartment_id:
            stock_shop_id = self.stock_balance.shop_id
            compartment_shop_id = self.compartment.area.shop_id

            if stock_shop_id != compartment_shop_id:
                raise ValidationError(
                    "Stock can only be allocated to a compartment in the same shop."
                )


# ============================================================
# CUSTOMERS, SALES, PAYMENTS, STOCK MOVEMENTS AND AUDIT
# ============================================================

class Customer(BaseModel):
    """A customer account scoped to one business."""
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name="customers")
    name = models.CharField(max_length=180)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["business", "phone"], condition=~models.Q(phone=""), name="unique_customer_phone_per_business")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Sale(BaseModel):
    """A confirmed checkout; child records are created in one database transaction."""
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        REVERSED = "REVERSED", "Reversed"

    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name="sales")
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="sales")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_sales")
    receipt_number = models.CharField(max_length=40, unique=True)
    idempotency_key = models.UUIDField(unique=True)
    currency = models.ForeignKey(BusinessCurrency, on_delete=models.PROTECT, related_name="sales")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)
    discount_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    pending_payment_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    confirmed_at = models.DateTimeField()

    class Meta:
        ordering = ["-confirmed_at"]

    def __str__(self):
        return self.receipt_number


class SaleItem(BaseModel):
    """Immutable product and price snapshot for a line on a sale."""
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    product_name = models.CharField(max_length=180)
    sku = models.CharField(max_length=80)
    quantity = models.DecimalField(max_digits=14, decimal_places=3, validators=[MinValueValidator(0.001)])
    unit_price = models.DecimalField(max_digits=14, decimal_places=2)
    line_total = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Payment(BaseModel):
    """Money actually received; credit is represented by the customer ledger."""
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
        BANK = "BANK", "Bank transfer"

    class Status(models.TextChoices):
        RECORDED = "RECORDED", "Recorded"
        PENDING = "PENDING", "Pending provider confirmation"
        CONFIRMED = "CONFIRMED", "Provider confirmed"
        FAILED = "FAILED", "Failed"
        REVERSED = "REVERSED", "Reversed"

    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="payments")
    method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0.01)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECORDED)
    reference = models.CharField(max_length=120, blank=True)
    received_at = models.DateTimeField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_payments")

    def __str__(self):
        return f"{self.sale.receipt_number}: {self.amount} {self.method}"


class CustomerLedgerEntry(BaseModel):
    """Append-only customer account entry; positive amounts increase debt."""
    class EntryType(models.TextChoices):
        SALE_CREDIT = "SALE_CREDIT", "Sale on credit"
        REPAYMENT = "REPAYMENT", "Customer repayment"
        ADJUSTMENT = "ADJUSTMENT", "Authorized adjustment"
        REVERSAL = "REVERSAL", "Reversal"

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="ledger_entries")
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="ledger_entries", null=True, blank=True)
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    currency = models.ForeignKey(BusinessCurrency, on_delete=models.PROTECT, related_name="customer_ledger_entries")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="customer_ledger_entries")

    class Meta:
        ordering = ["created_at"]


class StockMovement(BaseModel):
    """Append-only record explaining every stock quantity change."""
    class MovementType(models.TextChoices):
        SALE = "SALE", "Sale"
        RECEIPT = "RECEIPT", "Stock receipt"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        RETURN = "RETURN", "Return"
        TRANSFER_IN = "TRANSFER_IN", "Transfer in"
        TRANSFER_OUT = "TRANSFER_OUT", "Transfer out"

    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="stock_movements")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_movements")
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="stock_movements", null=True, blank=True)
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity_delta = models.DecimalField(max_digits=14, decimal_places=3)
    balance_after = models.DecimalField(max_digits=14, decimal_places=3)
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="stock_movements")


class AuditLog(BaseModel):
    """Trace important business actions without exposing secrets in logs."""
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name="audit_logs")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="business_audit_logs")
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=64)
    summary = models.CharField(max_length=255, blank=True)
