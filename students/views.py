# students/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
# In students/views.py (line 10)
# from timetable.models import Schedule  # Update 'Timetable' to match your model name
from .models import Student
from examinations.models import ExamResult
from finance.models import Invoice, MpesaTransactionLog
from communication.models import Notice

def my_student_view(request):
    from timetable.models import TimetableEntry
# A clean, fast verification decorator function to prevent role jumping
def student_required(view_func):
    from django.core.exceptions import PermissionDenied
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (getattr(request.user, 'role', '') == 'STUDENT' or hasattr(request.user, 'student_record')):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("Access Denied: This area is reserved for students.")
    return _wrapped_view


@login_required
@student_required
def student_portal_dashboard(request):
    # 1. Fetch the Student profile record linked to the logged-in User securely
    student = get_object_or_404(
        Student.objects.select_related('grade', 'stream'), 
        user=request.user
    )

    # 2. Grab Exam Results for this student
    exam_results = ExamResult.objects.filter(student=student).order_by('-created_at')[:10]

    # 3. Aggregate total fee rows cleanly via DB aggregates
    financial_summary = Invoice.objects.filter(student=student).aggregate(
        total_invoiced=Sum('total_amount'),
        total_paid=Sum('amount_paid')
    )

    total_invoiced = financial_summary['total_invoiced'] or 0.00
    total_paid = financial_summary['total_paid'] or 0.00
    ledger_balance = total_invoiced - total_paid

    # 4. Fetch Active Announcements targeting their specific Grade level
    notices = Notice.objects.filter(
        Q(target_grade=student.grade) | Q(target_grade__isnull=True)
    ).order_by('-created_at')[:5]

    # 5. Fetch Class Timetables matching their academic group
    schedules = Timetable.objects.filter(
        grade=student.grade, 
        stream=student.stream
    ).order_by('day_of_week', 'start_time')

    # 6. Fetch Recent M-Pesa Transaction History
    recent_payments = MpesaTransactionLog.objects.filter(student=student).order_by('-created_at')[:5]

    # 7. Construct unified context package
    context = {
        'student': student,
        'exam_results': exam_results,
        'schedules': schedules,
        'total_invoiced': f"{total_invoiced:,.2f}",
        'total_paid': f"{total_paid:,.2f}",
        'ledger_balance': f"{ledger_balance:,.2f}",
        'ledger_balance_raw': ledger_balance, # Useful for M-Pesa form defaults later
        'notices': notices,
        'recent_payments': recent_payments,
    }

    return render(request, 'students/dashboard.html', context)
