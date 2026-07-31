# accounts/urls.py
from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # Custom login layout that handles multi-role requests safely
    path('login/', views.login_view, name='login'),
    
    # Central redirection point that catches users after form submission
    path('dashboard/', views.dashboard_router, name='dashboard_router'),
    
    # Sub-routing hooks for parents portal management layout
    path("parents/", include("parents_portal.urls")),
]
