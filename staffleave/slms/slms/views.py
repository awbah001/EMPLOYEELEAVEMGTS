from django.shortcuts import render,redirect,HttpResponse
from slmsapp.EmailBackEnd import EmailBackEnd
from django.contrib.auth import authenticate, logout, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from slmsapp.models import CustomUser, SystemSettings
from django.core.cache import cache
from .auth_utils import validate_password, get_int_setting, increment_failed_attempts, is_locked_out, get_lockout_key, get_lockout_info_key
from django.db.models import Q

from django.contrib.auth import get_user_model
User = get_user_model()

def BASE(request):
    return render(request,'base.html')

def FIRSTPAGE(request):
    return redirect('login')

def LOGIN(request):
    return render(request,'login.html')

def doLogin(request):
    if request.method == 'POST':
        # basic lockout checks
        identifier = request.POST.get('email', '').strip().lower()
        ip = request.META.get('REMOTE_ADDR') or 'unknown'
        threshold = get_int_setting('login_lockout_threshold', 5)
        lock_minutes = get_int_setting('login_lockout_minutes', 15)

        if is_locked_out(identifier) or is_locked_out(ip):
            messages.error(request, 'Your account or IP is temporarily locked due to multiple failed login attempts. Please try again later.')
            return redirect('login')

        # Use Django's authenticate so the returned user has a backend attribute set
        user = authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user is not None:
            if not user.is_active:
                messages.error(request, 'This account is inactive. Please contact the administrator.')
                return redirect('login')
            login(request, user)
            # clear any recorded failed attempts on successful login
            try:
                cache.delete(get_lockout_key(identifier))
                cache.delete(get_lockout_info_key(identifier))
                cache.delete(get_lockout_key(ip))
                cache.delete(get_lockout_info_key(ip))
            except Exception:
                pass
            user_type = user.user_type
            if user_type == '1':  # Super Admin
                return redirect('superadmin_home')
            elif user_type == '2':  # Employee
                return redirect('staff_home')
            elif user_type == '3':  # Department Head
                return redirect('dh_home')
            elif user_type == '4':  # HR
                return redirect('hr_home')
            else:
                messages.error(request, 'Account type not recognized.')
                return redirect('login')
        else:
            # As a fallback, attempt to find a user by email or username and verify password
            identifier_value = request.POST.get('email', '').strip()
            password_value = request.POST.get('password', '')
            user_candidate = None
            try:
                # try email match first
                user_candidate = CustomUser.objects.get(email__iexact=identifier_value)
            except CustomUser.DoesNotExist:
                try:
                    user_candidate = CustomUser.objects.get(username__iexact=identifier_value)
                except CustomUser.DoesNotExist:
                    user_candidate = None

            if user_candidate and user_candidate.check_password(password_value):
                if not user_candidate.is_active:
                    messages.error(request, 'This account is inactive. Please contact the administrator.')
                    return redirect('login')
                # Explicitly set backend to the email backend so Django's login() accepts it
                user_candidate.backend = 'slmsapp.EmailBackEnd.EmailBackEnd'
                login(request, user_candidate)
                # clear lockout info
                try:
                    cache.delete(get_lockout_key(identifier))
                    cache.delete(get_lockout_info_key(identifier))
                    cache.delete(get_lockout_key(ip))
                    cache.delete(get_lockout_info_key(ip))
                except Exception:
                    pass
                # redirect according to role
                user_type = user_candidate.user_type
                if user_type == '1':
                    return redirect('superadmin_home')
                elif user_type == '2':
                    return redirect('staff_home')
                elif user_type == '3':
                    return redirect('dh_home')
                elif user_type == '4':
                    return redirect('hr_home')
                else:
                    messages.error(request, 'Account type not recognized.')
                    return redirect('login')

            # Increment failed counters for identifier and IP
            increment_failed_attempts(identifier, threshold, lock_minutes)
            increment_failed_attempts(ip, threshold, lock_minutes)
            messages.error(request, 'Email or Password is not valid')
            return redirect('login')
    else:
        messages.error(request, 'Email or Password is not valid')
        return redirect('login')
        


def doLogout(request):
    logout(request)
    return redirect('login')
@login_required(login_url='/')
def INDEX(request):
     return render(request,'index.html')

@login_required(login_url='/')
def PROFILE(request):
    user = CustomUser.objects.get(id = request.user.id)
    context = {
        "user":user,
    }
    return render(request,'profile.html',context)
@login_required(login_url = '/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        try:
            customuser = CustomUser.objects.get(id = request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if profile_pic !=None and profile_pic != "":
               customuser.profile_pic = profile_pic
            customuser.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, customuser)
            messages.success(request,"Your profile has been updated successfully")
            return redirect('profile')
        except Exception as e:
            print("Profile update error:", e)  # log the exception for debug
            messages.error(request,"Your profile updation has been failed")
    return render(request, 'profile.html')


@login_required(login_url='/')
def CHANGE_PASSWORD(request):
    context = {}
    ch = User.objects.filter(id=request.user.id)

    if ch.exists():
        data = User.objects.get(id=request.user.id)
        context['data'] = data

    if request.method == "POST":
        current = request.POST.get("cpwd")
        new_pas = request.POST.get('npwd')
        user = User.objects.get(id=request.user.id)
        if user.check_password(current):
            ok, msg = validate_password(new_pas)
            if not ok:
                messages.warning(request, msg)
                return redirect('change_password')

            user.set_password(new_pas)
            user.save()
            messages.success(request, 'Password changed successfully')
            # re-login the user so the session remains valid
            # Set the backend explicitly for email-based authentication
            user.backend = 'slmsapp.EmailBackEnd.EmailBackEnd'
            login(request, user)
            return redirect('change_password')
        else:
            messages.error(request, 'Current password is incorrect')
            return redirect('change_password')
    return render(request,'change-password.html', context)
