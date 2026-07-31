from django.shortcuts import render



# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...