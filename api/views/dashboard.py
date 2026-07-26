from rest_framework.views import APIView
from rest_framework.response import Response

from dashboard.services import DashboardService


class DashboardAPIView(APIView):

    def get(self, request):

        data = DashboardService.get_statistics()

        return Response(data)