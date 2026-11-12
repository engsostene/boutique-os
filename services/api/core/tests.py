from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    Business,
    BusinessGroup,
    BusinessMembership,
    BusinessRole,
    GroupBusinessLink,
    GroupMembership,
    MembershipRole,
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

        self.assertFalse(
            hasattr(self.business_a, "group_link")
        )

    def test_business_can_join_a_group_with_reporting_permissions(self):
        """Group reporting permissions are configurable."""

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
