from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ObjectDoesNotExist
from students.models import Student
from finance.models import Invoice
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...
@login_required
def parent_dashboard(request):
    context = {
        "portal_name": "Parents Portal Dashboard",
    }
    return render(request, "parents_portal/dashboard.html", context)

@login_required
def parent_dashboard(request):
    try:
        # Fetch the real student record linked via the OneToOne relationship
        student_profile = Student.objects.get(user=request.user)
        
        # Calculate real balances from your automated invoices
        unpaid_invoices = Invoice.objects.filter(student=student_profile).exclude(status='PAID')
        
        # Calculate total balance based on your fields: total_amount minus amount_paid
        total_balance = sum((inv.total_amount - inv.amount_paid) for inv in unpaid_invoices)
        
        students_data = [
            {
                "name": student_profile.full_name,
                "class": f"{student_profile.grade.name} - {student_profile.stream.name}",
                "admission_no": student_profile.admission_number,
                "gender": student_profile.gender,
                "status": student_profile.status,
                "fee_balance": f"KSh {total_balance:,.2f}",
                # Fallbacks for sections to add later
                "attendance": "95%", 
                "term_average": "A-",
            }
        ]
        
    except ObjectDoesNotExist:
        # Fallback if a manager or superuser views the page
        students_data = []

    context = {
        "portal_name": "DenTech Edu Parent Portal",
        "parent_name": f"Parent of {request.user.first_name or request.user.username}",
        "students": students_data,
        "announcements": [
            {"date": "July 31, 2026", "title": "End of Term Parent-Teacher Conference", "body": "Please join us at 9:00 AM to review term progress."},
            {"date": "August 5, 2026", "title": "Term 3 Fee Structure Release", "body": "Invoices for next term have been updated on the finance module."}
        ]
    }
    return render(request, "parents_portal/dashboard.html", context)


def parent_login_view(request):
    if request.method == "POST":
        admission = request.POST.get("username")
        upi = request.POST.get("password")

        # Routes credentials cleanly into our custom StudentCredentialsBackend
        user = authenticate(request, username=admission, password=upi)
        if user is not None:
            login(request, user)
            return redirect('/accounts/parents/dashboard/')
        else:
            messages.error(request, "Invalid Student Admission Number or UPI combination.")

    return render(request, "parents_portal/login.html")
