from django.contrib import admin
from .models import FeeStructure, Invoice, PaymentLog, MpesaTransactionLog, BankTransactionLog


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "term", "total_amount", "created_at")
    search_fields = ("name", "academic_year", "term")
    list_filter = ("academic_year", "term")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "student", "amount_due", "amount_paid", "status", "due_date")
    list_filter = ("status", "due_date", "created_at")
    search_fields = ("invoice_number", "student__first_name", "student__last_name", "student__admission_number")
    readonly_fields = ("status", "amount_paid", "created_at", "updated_at")


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ("transaction_reference", "invoice", "payment_method", "amount_received", "timestamp")
    list_filter = ("payment_method", "timestamp")
    search_fields = ("transaction_reference", "invoice__invoice_number")


@admin.register(MpesaTransactionLog)
class MpesaTransactionLogAdmin(admin.ModelAdmin):
    list_display = ("mpesa_receipt_number", "invoice", "amount", "phone_number", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("mpesa_receipt_number", "phone_number", "checkout_request_id")


@admin.register(BankTransactionLog)
class BankTransactionLogAdmin(admin.ModelAdmin):
    list_display = ("bank_reference_code", "bank_name", "student", "invoice", "amount", "status", "verified_by")
    list_filter = ("status", "bank_name", "deposit_date")
    search_fields = ("bank_reference_code", "student__first_name", "student__last_name")