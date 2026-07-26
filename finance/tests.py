from decimal import Decimal
from datetime import date

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from academics.models import Grade, Stream
from finance.models import FeeStructure, Invoice, PaymentLog
from finance.views import payment_webhook
from students.models import Student


class BillingWorkflowTests(TestCase):
    def setUp(self):
        self.grade = Grade.objects.create(name="Grade 1")
        self.stream = Stream.objects.create(grade=self.grade, name="A")
        self.student = Student.objects.create(
            admission_number="ADM001",
            first_name="Amina",
            middle_name="",
            last_name="Kariuki",
            gender="Female",
            date_of_birth=date(2012, 5, 10),
            birth_certificate_number="BC001",
            grade=self.grade,
            stream=self.stream,
            admission_date=date(2024, 1, 15),
            status="Active",
        )

    def test_generate_monthly_invoices_creates_missing_invoices_without_duplicates(self):
        FeeStructure.objects.create(
            grade_level=self.grade.name,
            tuition_fee=Decimal("5000.00"),
            activity_fee=Decimal("300.00"),
            transport_fee=Decimal("200.00"),
        )

        call_command("generate_monthly_invoices")
        call_command("generate_monthly_invoices")

        invoices = Invoice.objects.filter(student=self.student)
        self.assertEqual(invoices.count(), 1)
        invoice = invoices.get()
        self.assertEqual(invoice.total_amount, Decimal("5500.00"))
        self.assertEqual(invoice.amount_paid, Decimal("0.00"))
        self.assertEqual(invoice.status, "UNPAID")

    def test_webhook_reconciliation_updates_balance_and_payment_log(self):
        invoice = Invoice.objects.create(
            student=self.student,
            billing_month=date(2026, 7, 1),
            total_amount=Decimal("1000.00"),
            amount_paid=Decimal("100.00"),
            status="PARTIAL",
        )

        factory = APIRequestFactory()
        request = factory.post(
            "/finance/webhook/",
            {
                "invoice_id": invoice.id,
                "transaction_reference": "TXN-100",
                "amount": "300.00",
                "status": "PARTIAL",
                "payment_method": "MPESA",
            },
            format="json",
        )

        response = payment_webhook(request)

        self.assertEqual(response.status_code, 200)
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("400.00"))
        self.assertEqual(invoice.balance_due, Decimal("600.00"))
        self.assertEqual(invoice.status, "PARTIAL")
        self.assertTrue(
            PaymentLog.objects.filter(
                invoice=invoice,
                transaction_reference="TXN-100",
                amount_received=Decimal("300.00"),
            ).exists()
        )
