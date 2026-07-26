from rest_framework import serializers

from .models import FeeStructure, Invoice, PaymentLog


class FeeStructureSerializer(serializers.ModelSerializer):
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = FeeStructure
        fields = ["id", "grade_level", "tuition_fee", "activity_fee", "transport_fee", "total_amount"]


class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLog
        fields = ["id", "transaction_reference", "amount_received", "payment_method", "timestamp"]


class InvoiceSerializer(serializers.ModelSerializer):
    balance_due = serializers.ReadOnlyField()
    payment_logs = PaymentLogSerializer(many=True, read_only=True, source="payment_logs")

    class Meta:
        model = Invoice
        fields = [
            "id",
            "student",
            "billing_month",
            "total_amount",
            "amount_paid",
            "balance_due",
            "status",
            "created_at",
            "updated_at",
            "payment_logs",
        ]
