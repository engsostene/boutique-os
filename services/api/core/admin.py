from django.contrib import admin

from .models import (
    AuditLog, Customer, CustomerLedgerEntry, Payment, Sale, SaleItem,
    StockMovement,
)


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("product", "product_name", "sku", "quantity", "unit_price", "line_total")
    can_delete = False


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("method", "amount", "status", "reference", "received_at", "recorded_by")
    can_delete = False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "business", "shop", "customer", "total", "amount_paid", "balance_due", "status", "confirmed_at")
    list_filter = ("status", "currency", "confirmed_at")
    search_fields = ("receipt_number", "customer__name", "customer__phone")
    readonly_fields = tuple(field.name for field in Sale._meta.fields)
    inlines = (SaleItemInline, PaymentInline)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "phone", "credit_limit", "is_active")
    list_filter = ("business", "is_active")
    search_fields = ("name", "phone", "email")


@admin.register(CustomerLedgerEntry)
class CustomerLedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("customer", "entry_type", "currency", "amount", "sale", "created_at")
    list_filter = ("entry_type", "currency", "created_at")
    search_fields = ("customer__name", "sale__receipt_number", "description")
    readonly_fields = tuple(field.name for field in CustomerLedgerEntry._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "shop", "movement_type", "quantity_delta", "balance_after", "sale", "created_by", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("product__name", "product__sku", "sale__receipt_number")
    readonly_fields = tuple(field.name for field in StockMovement._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("business", "actor", "action", "object_type", "object_id", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("object_id", "summary", "actor__username")
    readonly_fields = tuple(field.name for field in AuditLog._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method == "GET"

    def has_delete_permission(self, request, obj=None):
        return False
