from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def no_cache(view_func):
    """
    Decorator to prevent caching of authenticated pages.
    Prevents users from accessing pages via browser back button after logout.
    Sets cache headers: no-cache, no-store, must-revalidate, private, max-age=0
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0, post-check=0, pre-check=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        response['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        response['Vary'] = 'Cookie'
        if 'ETag' in response:
            del response['ETag']
        return response
    return wrapper

def role_required(*allowed_roles):
    """
    Decorator to check if user has required role(s)
    Usage: @role_required('1', '2') for Super Admin and Employee
    Automatically prevents caching to protect authenticated pages
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
            
            response = view_func(request, *args, **kwargs)
            # Apply aggressive no-cache headers to prevent browser caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0, post-check=0, pre-check=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            response['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            response['Vary'] = 'Cookie'
            if 'ETag' in response:
                del response['ETag']
            return response
        return wrapper
    return decorator

def super_admin_required(view_func):
    """Decorator to check if user is Super Admin (deprecated - use admin_required)"""
    return role_required('1')(view_func)

def admin_required(view_func):
    """Decorator to check if user is Admin (user_type = '1')"""
    return role_required('1')(view_func)

def employee_required(view_func):
    """Decorator to check if user is Employee"""
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

