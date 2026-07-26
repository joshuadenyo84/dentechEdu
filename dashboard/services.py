from students.models import Student
from teachers.models import Teacher
from academics.models import Grade, Stream, Subject


class DashboardService:

    @staticmethod
    def get_statistics():

        return {

            "students": Student.objects.count(),

            "teachers": Teacher.objects.count(),

            "grades": Grade.objects.count(),

            "streams": Stream.objects.count(),

            "subjects": Subject.objects.count(),

        }