from django.urls import path
from . import views

app_name = 'parents_portal'

urlpatterns = [
    path('dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('portal-login/', views.parent_login_view, name='portal_login'),

]
