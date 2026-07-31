from django.shortcuts import render
from accounts.decorators import permission_required_for_role

# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...
# Requires ALL permissions listed:
@permission_required_for_role('examinations.add_examresult', 'examinations.change_examresult')
def edit_results(request):
    ...

# Requires ANY of the permissions listed:
@permission_required_for_role('students.view_student', 'parents.view_student', any_permission=True)
def view_student_profile(request, student_id):
    ...