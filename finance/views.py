from decimal import Decimal

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import FeeStructure, Invoice, PaymentLog
from .serializers import FeeStructureSerializer, InvoiceSerializer

# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...

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


import base64
import requests
from datetime import datetime
import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from students.models import Student
from .models import Invoice # Assuming Invoice tracks balances

# -------------------------------------------------------------
# HELPER: Generate Access Token & STK Password Password
# -------------------------------------------------------------
def get_mpesa_access_token():
    url = "https://safaricom.co.ke"
    if settings.MPESA_ENVIRONMENT == 'production':
        url = "https://safaricom.co.ke"
        
    response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')

def generate_stk_password(timestamp):
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    return base64.b64encode(data_to_encode.encode()).decode('utf-8')

# -------------------------------------------------------------
# ENDPOINT 1: Initiate STK Push Payment Request
# -------------------------------------------------------------
@login_required
def initiate_stk_push(request):
    if request.method == 'POST':
        # 1. Identify student and phone number safely
        student = get_object_or_404(Student, user=request.user)
        
        # Pull phone number from guardian or student profile (format: 2547XXXXXXXX)
        # For testing, ensure your phone variable matches a valid safari format line
        phone_number = request.POST.get('phone_number') # e.g., "254712345678"
        amount = int(float(request.POST.get('amount'))) # M-Pesa API expects an integer string
        
        # 2. Setup structural variables
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = generate_stk_password(timestamp)
        access_token = get_mpesa_access_token()
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        url = "https://safaricom.co.ke" # Sandbox fallback
        if settings.MPESA_ENVIRONMENT == 'sandbox':
            url = "https://safaricom.co.ke"
        elif settings.MPESA_ENVIRONMENT == 'production':
            url = "https://safaricom.co.ke"

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": student.admission_number,
            "TransactionDesc": f"Fee Payment {student.admission_number}"
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        # CheckoutResponseCode '0' means the user was successfully prompted for their PIN
        if response_data.get('ResponseCode') == '0':
            return JsonResponse({'status': 'success', 'message': 'PIN prompt sent to phone.'})
        return JsonResponse({'status': 'error', 'message': response_data.get('ResponseDescription')})

    return JsonResponse({'status': 'error', 'message': 'Invalid Request Method.'})

# -------------------------------------------------------------
# ENDPOINT 2: Safaricom Public Callback Webhook Hook
# -------------------------------------------------------------
@csrf_exempt # Mandatory because Safaricom does not provide a Django CSRF token
def mpesa_callback(request):
    if request.method == 'POST':
        callback_data = json.loads(request.body.decode('utf-8'))
        
        # Extract response parameters
        stk_callback = callback_data['Body']['stkCallback']
        result_code = stk_callback['ResultCode']
        merchant_request_id = stk_callback['MerchantRequestID']
        checkout_request_id = stk_callback['CheckoutRequestID']
        
        # ResultCode 0 represents a completely cleared transaction
        if result_code == 0:
            metadata_items = stk_callback['CallbackMetadata']['Item']
            
            # Helper logic to extract individual item values out of nested schema lists
            mpesa_receipt = next(item['Value'] for item in metadata_items if item['Name'] == 'MpesaReceiptNumber')
            amount_paid = next(item['Value'] for item in metadata_items if item['Name'] == 'Amount')
            phone_paying = next(item['Value'] for item in metadata_items if item['Name'] == 'PhoneNumber')
            
            # Use AccountReference payload string pattern to look up matching record indexes
            # This relies on your reference being exactly the Admission Number
            admission_no = stk_callback['ResultDesc'].split()[-1] # Fallback parse strategy or pass via structural custom logic
            
            # Alternatively, find invoices using standard transaction model registers tied to CheckoutRequestID
            # For demonstration, we update the first matching unpaid invoice ledger row
            try:
                # Update ledger context logic
                invoice = Invoice.objects.filter(student__admission_number=admission_no, status='UNPAID').first()
                if invoice:
                    invoice.amount_paid += decimal.Decimal(amount_paid)
                    if invoice.amount_paid >= invoice.total_amount:
                        invoice.status = 'PAID'
                    invoice.save()
            except Exception as e:
                pass # Log database entry connection errors safely here
                
        # Always return a 200 OK acceptance string response block directly back to Safaricom
        return HttpResponse(json.dumps({"ResultCode": 0, "ResultDesc": "Accepted"}), content_type="application/json")
        
    return HttpResponse("Method not allowed", status=405)
