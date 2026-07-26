from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FeeStructureViewSet, InvoiceViewSet, payment_webhook

router = DefaultRouter()
router.register(r"fee-structures", FeeStructureViewSet, basename="fee-structure")
router.register(r"invoices", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", payment_webhook, name="finance-payment-webhook"),
]


