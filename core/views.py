# accounts/views.py (or core/views.py)
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages


# ✅ Good (Inside function)
def my_student_view(request):
    from timetable.models import TimetableEntry
    # ...

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # --- ROLE-BASED REDIRECT LOGIC ---
            if user.is_superuser or user.is_staff:
                return redirect("/admin/")
            elif hasattr(user, 'role'):
                if user.role == "STUDENT":
                    return redirect("students:dashboard")  # Adjust URL name
                elif user.role == "TEACHER":
                    return redirect("teachers:dashboard")  # Adjust URL name
                elif user.role == "PARENT":
                    return redirect("parents:dashboard")   # Adjust URL name
            
            # Fallback for default users
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "registration/login.html")