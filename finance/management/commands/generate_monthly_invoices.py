from decimal import Decimal
from datetime import date

from django.core.management.base import BaseCommand

from finance.models import FeeStructure, Invoice
from students.models import Student


class Command(BaseCommand):
    help = "Generate monthly invoices for active students based on the latest fee structure." 

    def handle(self, *args, **options):
        billing_month = date.today().replace(day=1)
        structure = FeeStructure.objects.order_by("id").first()
        if not structure:
            self.stdout.write(self.style.WARNING("No fee structure found; skipping invoice generation."))
            return

        active_students = Student.objects.filter(status="Active")
        created = 0
        for student in active_students:
            invoice, was_created = Invoice.objects.get_or_create(
                student=student,
                billing_month=billing_month,
                defaults={
                    "total_amount": structure.total_amount,
                    "amount_paid": Decimal("0.00"),
                    "status": "UNPAID",
                },
            )
            if was_created:
                created += 1
                invoice.total_amount = structure.total_amount
                invoice.amount_paid = Decimal("0.00")
                invoice.status = "UNPAID"
                invoice.save()

        self.stdout.write(self.style.SUCCESS(f"Generated {created} invoices for {active_students.count()} active students."))
