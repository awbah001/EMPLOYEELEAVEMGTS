from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(*allowed_roles):
    """
    Decorator to check if user has required role(s)
    Usage: @role_required('1', '2') for Super Admin and Staff
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('login')
            
            user_type = str(request.user.user_type)
            if user_type not in allowed_roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def super_admin_required(view_func):
    """Decorator to check if user is Super Admin (deprecated - use admin_required)"""
    return role_required('1')(view_func)

def admin_required(view_func):
    """Decorator to check if user is Admin (user_type = '1')"""
    return role_required('1')(view_func)

def staff_required(view_func):
    """Decorator to check if user is Staff"""
    return role_required('2')(view_func)

def department_head_required(view_func):
    """Decorator to check if user is Department Head"""
    return role_required('3')(view_func)

def hr_required(view_func):
    """Decorator to check if user is HR"""
    return role_required('4')(view_func)

def admin_or_hr_required(view_func):
    """Decorator to check if user is Super Admin or HR"""
    return role_required('1', '4')(view_func)

