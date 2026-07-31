from django.shortcuts import render

def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...