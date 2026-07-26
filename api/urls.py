from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.student import StudentViewSet
from api.views.dashboard import DashboardAPIView

router = DefaultRouter()

router.register(
    "students",
    StudentViewSet,
    basename="students",
)

urlpatterns = [

    path("", include(router.urls)),
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
]