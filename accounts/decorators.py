# accounts/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def permission_required_for_role(*perm_codes, any_permission=False):
    """
    Checks if the user's assigned dynamic role possesses specific Django permissions.
    
    Supports checking a single permission or a list of permissions.
    
    Examples:
        @permission_required_for_role('examinations.add_examresult')
        @permission_required_for_role('students.change_student', 'students.delete_student', any_permission=True)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Redirect anonymous users to the login page cleanly
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            # 2. Universal bypass for superusers
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 3. Evaluate permissions dynamically against Django's backend
            if any_permission:
                # Passes if the user has AT LEAST ONE of the listed permissions
                has_access = any(request.user.has_perm(perm) for perm in perm_codes)
            else:
                # Passes only if the user has ALL listed permissions (Default)
                has_access = all(request.user.has_perm(perm) for perm in perm_codes)

            if has_access:
                return view_func(request, *args, **kwargs)

            # 4. Block authenticated users without the right role permissions
            raise PermissionDenied("Your current role does not have permission to access this resource.")

        return _wrapped_view
    return decorator