# students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Clean dashboard route matching our accounts view definitions
    path('dashboard/', views.student_portal_dashboard, name='dashboard'),
]
