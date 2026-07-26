from rest_framework import viewsets

from students.models import Student

from api.serializers.student import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):

    queryset = Student.objects.select_related(
        "grade",
        "stream",
    )

    serializer_class = StudentSerializer

    search_fields = [
        "admission_number",
        "first_name",
        "last_name",
    ]

    filterset_fields = [
        "grade",
        "stream",
        "gender",
        "status",
    ]

    ordering_fields = "__all__"