from decimal import Decimal
from django.db import models
from academics.models import Grade, Term  # Connected to foundation layer
from students.models import Student


class FeeStructure(models.Model):
    # Linked directly to your actual Grade master registry instead of plain text
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="fee_structures", db_column="grade_level")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="fee_structures", null=True, blank=True)
    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    activity_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    transport_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["grade"]
        # Prevents setting up multiple duplicate conflicting price structures for the same class term
        unique_together = ("grade", "term")

    @property
    def total_amount(self):
        return self.tuition_fee + self.activity_fee + self.transport_fee

    def __str__(self):
        term_name = self.term.name if self.term else "Global"
        return f"{self.grade.name} - ({term_name})"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("UNPAID", "Unpaid"),
        ("PARTIAL", "Partially Paid"),
        ("PAID", "Paid"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="invoices")
    billing_month = models.DateField()
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="invoices", null=True, blank=True)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="UNPAID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-billing_month", "student__admission_number"]
        unique_together = ("student", "billing_month")

    @property
    def balance_due(self):
        total = self.total_amount or Decimal("0.00")
        paid = self.amount_paid or Decimal("0.00")
        return max(total - paid, Decimal("0.00"))

    def recalculate_status(self):
        total = self.total_amount or Decimal("0.00")
        paid = self.amount_paid or Decimal("0.00")
        
        if paid <= 0:
            return "UNPAID"
        if paid >= total:
            return "PAID"
        return "PARTIAL"

    def save(self, *args, **kwargs):
        # Dynamically recalculate payment status indicators whenever changes occur
        self.status = self.recalculate_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.id} - {self.student} - {self.billing_month:%B %Y}"


class PaymentLog(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payment_logs")
    transaction_reference = models.CharField(max_length=100, unique=True)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    payment_method = models.CharField(max_length=50, default="MPESA")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.transaction_reference

# Append this logic directly onto the bottom of your finance/models.py file
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=PaymentLog)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    """
    Listens for any incoming recorded transaction receipts (M-PESA/Bank).
    Instantly recalculates and updates the core Student Invoice record.
    """
    if created:
        invoice = instance.invoice
        # Aggregate all payments logged against this specific invoice instance row
        all_payments = PaymentLog.objects.filter(invoice=invoice)
        total_paid = sum(payment.amount_received for payment in all_payments)
        
        # Write fresh updates to invoice record
        invoice.amount_paid = total_paid
        invoice.status = invoice.recalculate_status()
        invoice.save()

# Append to the absolute bottom of finance/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=PaymentLog)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    """
    Listens for any new PaymentLog entry.
    Instantly sums up payment history records and recalculates the Invoice balances.
    """
    if created:
        invoice = instance.invoice
        # Calculate all recorded cash collection rows tied to this invoice instance
        all_payments = PaymentLog.objects.filter(invoice=invoice)
        total_paid = sum(payment.amount_received for payment in all_payments)
        
        # Update the parent tracking ledger values
        invoice.amount_paid = total_paid
        invoice.status = invoice.recalculate_status()
        invoice.save()
