import urllib.parse
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from students.models import Student
from .models import FeeStructure, Invoice, PaymentLog


class TenantBaseAdmin(admin.ModelAdmin):
    """
    Custom Base Admin ensuring that when an admin views records,
    the queries honor our isolated multi-database routing setup.
    """
    def save_model(self, request, obj, form, change):
        db = request.headers.get('X-School-DB') or 'default'
        obj.save(using=db)

    def delete_model(self, request, obj):
        db = request.headers.get('X-School-DB') or 'default'
        obj.delete(using=db)

    def get_queryset(self, request):
        db = request.headers.get('X-School-DB') or 'default'
        return super().get_queryset(request).using(db)


@admin.register(FeeStructure)
class FeeStructureAdmin(TenantBaseAdmin):  # Inherits multi-tenant isolation
    list_display = ("grade", "term", "tuition_fee", "activity_fee", "transport_fee", "display_total")
    list_filter = ("grade", "term")
    search_fields = ("grade__name",)

    def display_total(self, obj):
        return f"KES {obj.total_amount:,.2f}"
    display_total.short_description = "Total Fee"


# Open finance/admin.py and replace your InvoiceAdmin setup with this block:

@admin.register(Invoice)
class InvoiceAdmin(TenantBaseAdmin):
    list_display = ("id", "student", "term", "billing_month", "display_total", "display_paid", "display_balance", "colored_status")
    list_filter = ("status", "term", "billing_month")
    search_fields = ("student__admission_number", "student__user__first_name", "student__user__last_name")
    readonly_fields = ("status",)

    def get_queryset(self, request):
        """Filters visibility fields depending entirely on active profile roles."""
        qs = super().get_queryset(request)
        user = request.user
        
        if not user.is_authenticated:
            return qs.none()
            
        # Role Permissions Engine Matrix
        if user.is_superuser or user.role == 'ADMIN':
            return qs  # Administrators maintain complete oversight across every record
            
        if user.role in ['PRINCIPAL', 'DEPUTY', 'ACCOUNTANT']:
            return qs  # Executives and Accountants maintain clear visibility access
            
        return qs.none()  # Block teachers, library clerks, parents, or students from accessing financial rows

    def has_add_permission(self, request):
        """Only system admins and accountants can create manual invoices."""
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role in ['ADMIN', 'ACCOUNTANT']:
            return True
        return False  # Principals & deputies see data but cannot create invoices manually

    def has_change_permission(self, request, obj=None):
        """Blocks principals and deputies from altering established historical balances."""
        if not request.user.is_authenticated:
            return False
        if request.user.role in ['PRINCIPAL', 'DEPUTY']:
            return False  # Read-Only view access for executives
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Restricts financial record deletion strictly to system super-administrators."""
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role == 'ADMIN':
            return True
        return False  # Accountants and principals can NEVER completely delete an invoice trail

    # Re-paste your clean layout formatting helpers below:
    def display_total(self, obj):
        return f"KES {obj.total_amount:,.2f}"
    display_total.short_description = "Total Due"

    def display_paid(self, obj):
        return f"KES {obj.amount_paid:,.2f}"
    display_paid.short_description = "Paid"

    def display_balance(self, obj):
        return f"KES {obj.balance_due:,.2f}"
    display_balance.short_description = "Balance"

    def colored_status(self, obj):
        colors = {"PAID": "#28a745", "PARTIAL": "#ffc107", "UNPAID": "#dc3545"}
        text_color = "#000" if obj.status == "PARTIAL" else "#fff"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.status, "#6c757d"), text_color, obj.get_status_display()
        )
    colored_status.short_description = "Status"



@admin.register(PaymentLog)
class PaymentLogAdmin(TenantBaseAdmin):  # Inherits multi-tenant isolation
    list_display = ("invoice", "transaction_reference", "display_amount", "payment_method", "timestamp")
    list_filter = ("payment_method", "timestamp")
    search_fields = ("transaction_reference", "invoice__id")

    def display_amount(self, obj):
        return f"KES {obj.amount_received:,.2f}"
    display_amount.short_description = "Amount Received"
