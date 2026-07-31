from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# ==========================================
# 📄 FEE STRUCTURE & INVOICE MODELS
# ==========================================

class FeeStructure(models.Model):
    """
    Defines fee components (e.g., Tuition, Lab Fees, Library) per term or academic year.
    """
    name = models.CharField(max_length=100, help_text="e.g., Term 1 Tuition Fee")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    academic_year = models.CharField(max_length=20, help_text="e.g., 2026")
    term = models.CharField(max_length=20, help_text="e.g., Term 1")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.academic_year} - {self.term})"


class Invoice(models.Model):
    """
    Student Invoices generated based on fee structures.
    """
    class StatusChoices(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIAL = "PARTIAL", "Partially Paid"
        PAID = "PAID", "Fully Paid"
        OVERDUE = "OVERDUE", "Overdue"

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name="invoices")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices")
    invoice_number = models.CharField(max_length=50, unique=True, help_text="Unique invoice reference number")
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.UNPAID)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.student}"

    @property
    def balance(self):
        return self.amount_due - self.amount_paid


# ==========================================
# 💳 PAYMENT LOGS & MODES REGISTRY
# ==========================================

class PaymentLog(models.Model):
    """
    Unified School Revenue Ledger. 
    Every single cent collected by the institution MUST land here, regardless of channel.
    """
    class PaymentMethods(models.TextChoices):
        MPESA = "MPESA", "M-Pesa STK/Paybill"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Deposit / EFT"
        CASH = "CASH", "Direct Cash Payment"
        CHEQUE = "CHEQUE", "Cheque Payment"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payment_logs")
    transaction_reference = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Unique Identifier (e.g., M-Pesa Code or Bank Slip Reference)"
    )
    amount_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethods.choices, 
        default=PaymentMethods.MPESA
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["payment_method"]),
        ]

    def __str__(self):
        return f"{self.payment_method} | {self.transaction_reference} - {self.amount_received}"


# ==========================================
# 📱 M-PESA TRANSACTION LOGGING
# ==========================================

class MpesaTransactionLog(models.Model):
    """
    Tracks incoming M-Pesa STK Push and C2B payment webhook payloads.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name="mpesa_transactions")
    mpesa_receipt_number = models.CharField(max_length=50, unique=True, help_text="The unique M-Pesa transaction code")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=20, default="Success", help_text="Success, Failed, Pending")
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    result_desc = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"M-Pesa {self.mpesa_receipt_number} - {self.amount} [{self.status}]"


# ==========================================
# 🏦 BANK TRANSACTION LOGGING
# ==========================================

class BankTransactionLog(models.Model):
    """
    Tracks offline bank direct deposits and transfers requiring manual admin verification.
    """
    STATUS_CHOICES = (
        ("Pending", "Pending Verification"),
        ("Approved", "Approved & Cleared"),
        ("Rejected", "Rejected / Invalid Reference"),
    )

    student = models.ForeignKey('students.Student', on_delete=models.PROTECT, related_name="bank_payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, blank=True, null=True, related_name="bank_transactions")
    
    bank_name = models.CharField(max_length=100, help_text="e.g., KCB, Equity Bank, Co-op Bank")
    bank_reference_code = models.CharField(max_length=50, unique=True, help_text="The transaction code from the bank receipt")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    deposit_date = models.DateField(help_text="Date stamped on the physical deposit slip")
    
    slip_image = models.FileField(upload_to="bank_slips/%Y/%m/", blank=True, null=True, help_text="Scan/Photo of deposit slip")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="Pending")
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name="verified_slips"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Bank ({self.bank_name}) - {self.bank_reference_code} [{self.status}]"


# ==========================================
# 🤖 AUTOMATION WORKFLOW SIGNALS
# ==========================================

@receiver(post_save, sender=MpesaTransactionLog)
def convert_successful_mpesa_to_ledger(sender, instance, created, **kwargs):
    """
    Automated Webhook Link.
    When your API signals a successful M-Pesa transaction, instantly populate the central log.
    """
    if instance.status == "Success" and instance.invoice:
        PaymentLog.objects.get_or_create(
            transaction_reference=instance.mpesa_receipt_number,
            defaults={
                'invoice': instance.invoice,
                'amount_received': instance.amount,
                'payment_method': PaymentLog.PaymentMethods.MPESA
            }
        )


@receiver(post_save, sender=BankTransactionLog)
def convert_approved_bank_slip_to_ledger(sender, instance, **kwargs):
    """
    Administrative Approval Link.
    """
    if instance.status == "Approved" and instance.invoice:
        PaymentLog.objects.get_or_create(
            transaction_reference=instance.bank_reference_code,
            defaults={
                'invoice': instance.invoice,
                'amount_received': instance.amount,
                'payment_method': PaymentLog.PaymentMethods.BANK_TRANSFER
            }
        )
    elif instance.status in ["Pending", "Rejected"] and instance.invoice:
        PaymentLog.objects.filter(transaction_reference=instance.bank_reference_code).delete()