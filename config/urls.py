from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Custom Admin Branding Panel Configurations
admin.site.site_header = "DENTECHSYSTEMS"
admin.site.site_title = "Dentechsystems Portal"
admin.site.index_title = "Welcome to Dentechsystems Management System"


def homepage_view(request):
    """Render a clean, modern landing page for the application."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome | Dentechsystems</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f7fafc;
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                color: #2d3748;
            }
            .card {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
                text-align: center;
                max-width: 450px;
                width: 100%;
                box-sizing: border-box;
            }
            h1 {
                color: #2b6cb0;
                margin-bottom: 10px;
                font-size: 2rem;
            }
            p {
                color: #718096;
                margin-bottom: 30px;
                line-height: 1.6;
            }
            .btn-group {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .btn {
                display: block;
                padding: 12px 30px;
                background: #2b6cb0;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                transition: background 0.2s;
            }
            .btn:hover {
                background: #2c5282;
            }
            .btn-alt {
                background: #4a5568;
            }
            .btn-alt:hover {
                background: #2d3748;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Dentechsystems</h1>
            <p>The core school management portal engine is running smoothly. Welcome back!</p>
            <div class="btn-group">
                <a href="/admin/" class="btn btn-alt">Go to Admin Dashboard</a>
                <a href="/accounts/login/" class="btn">Portal Sign In</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)


urlpatterns = [
    # Static Assets Router (Stops browser favicon.ico 404 log spam)
    path(
        "favicon.ico",
        RedirectView.as_view(
            url="data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            permanent=True,
        ),
    ),
    
    # Root Homepage Landing Route
    path("", homepage_view, name="home"),
    
    # Django Administrative Management Suite
    path("admin/", admin.site.urls),

    # Core REST Framework Endpoints
    path("api/", include("api.urls")),
    path("api/finance/", include("finance.urls")),
    
    # API Documentation Engines
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    
    # JSON Web Token Security Auth Engine
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    
    # Connect Multi-Role System Authentication & Portals
    path("accounts/", include("accounts.urls")),
    path("students/", include("students.urls")), # Directs traffic into your student portal app routes
]

