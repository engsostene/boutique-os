import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


# ============================================================
# COMMON MODEL BASE
# ============================================================

class BaseModel(models.Model):
    """Shared identifiers and timestamps for business records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================
# BUSINESS GROUP AND OPTIONAL GROUP REPORTING
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
    """
    Optional link between a business and a group.

    Reporting access is explicitly configurable. Linking a business
    to a group does not automatically expose all its information.
    """

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

    def __str__(self):
        return f"{self.business} → {self.group}"

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
# BUSINESS USERS, ROLES AND PERMISSIONS
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
