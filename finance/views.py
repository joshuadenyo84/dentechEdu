from decimal import Decimal

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import FeeStructure, Invoice, PaymentLog
from .serializers import FeeStructureSerializer, InvoiceSerializer


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def payment_webhook(request):
    payload = request.data or {}
    invoice_id = payload.get("invoice_id")
    transaction_reference = payload.get("transaction_reference")
    amount = payload.get("amount")
    status_value = payload.get("status")

    if not invoice_id or not transaction_reference or amount is None:
        return Response({"detail": "invoice_id, transaction_reference, and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invoice = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return Response({"detail": "invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        amount_received = Decimal(str(amount))
    except Exception:
        return Response({"detail": "amount must be numeric"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        invoice.amount_paid = (invoice.amount_paid or Decimal("0.00")) + amount_received
        invoice.status = status_value or invoice.recalculate_status()
        invoice.save()

        PaymentLog.objects.create(
            invoice=invoice,
            transaction_reference=transaction_reference,
            amount_received=amount_received,
            payment_method=payload.get("payment_method", "MPESA"),
        )

    invoice.refresh_from_db()
    return Response({
        "invoice_id": invoice.id,
        "amount_paid": str(invoice.amount_paid),
        "balance_due": str(invoice.balance_due),
        "status": invoice.status,
    }, status=status.HTTP_200_OK)
