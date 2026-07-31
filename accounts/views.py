# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages

# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...
@login_required
def dashboard_router(request):
    user = request.user
    
    # 1. Route Admin & Staff users straight to the main panel
    if user.is_superuser or user.is_staff or user.role == "ADMIN":
        return redirect('/admin/')
        
    # 2. Route Students to their dedicated app space
    if getattr(user, 'role', None) == "STUDENT" or hasattr(user, 'student_record'):
        return redirect('students:dashboard') # Triggers the student portal app view!
        
    # 3. Route Parents to their portal space
    if getattr(user, 'role', None) == "PARENT":
        return redirect('/accounts/parents/dashboard/')
        
    # Fallback to homepage if role is undetermined
    return redirect('home')


def login_view(request):
    """Renders a production-ready, clean credential gateway processing engine."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_router')

    if request.method == 'POST':
        # Extract inputs directly from POST to bypass standard strict username restrictions
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            messages.error(request, "Please fill in all credential fields.")
            return render(request, 'accounts/login.html')

        # This loops through all backends in AUTHENTICATION_BACKENDS securely
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('accounts:dashboard_router')
        else:
            messages.error(request, "Invalid Admission Number, Username, or Password.")
            
    return render(request, 'accounts/login.html')

