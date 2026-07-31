from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, InvoiceViewSet, payment_webhook
from django.urls import path
from . import views

router = DefaultRouter()
router.register(r"fee-structures", FeeStructureViewSet, basename="fee-structure")
router.register(r"invoices", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("", include(router.urls)),
    path("webhook/", payment_webhook, name="finance-payment-webhook"),

    path('mpesa/initiate/', views.initiate_stk_push, name='initiate_stk_push'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]

# urls.py
from django.views.generic.base import RedirectView
from django.templatetags.static import static

urlpatterns = [
    # Point directly to a static file URL path, not a data: string
    path('favicon.ico', RedirectView.as_view(url=static('images/favicon.ico'), permanent=True)),
]