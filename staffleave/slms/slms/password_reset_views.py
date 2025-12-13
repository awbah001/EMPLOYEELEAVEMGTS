import random
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View

from .auth_utils import validate_password

User = get_user_model()


def _otp_cache_key(email: str) -> str:
    return f'password_reset_otp_{email.lower()}'


def _generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def _get_from_email() -> str:
    return getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'noreply@example.com'


OTP_EXPIRY_MINUTES = getattr(settings, 'PASSWORD_RESET_OTP_TIMEOUT', 10)
OTP_MAX_ATTEMPTS = getattr(settings, 'PASSWORD_RESET_OTP_ATTEMPTS', 5)


class OTPRequestForm(forms.Form):
    email = forms.EmailField(label='Email address', max_length=254)


class OTPVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    otp = forms.CharField(label='Verification code', max_length=6, min_length=6)


class CustomSetPasswordForm(SetPasswordForm):
    """Extend SetPasswordForm to include system password rules."""

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        if password1:
            ok, msg = validate_password(password1)
            if not ok:
                self.add_error('new_password1', forms.ValidationError(msg))
        return cleaned_data


class OTPPasswordResetView(View):
    """
    Step 1: Collect user email and send a time-bound OTP to verify ownership.
    """

    template_name = 'registration/password_reset.html'

    def get(self, request):
        email = request.session.get('password_reset_email', '')
        form = OTPRequestForm(initial={'email': email})
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = OTPRequestForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        email = form.cleaned_data['email']
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            form.add_error('email', 'No active account found with this email.')
            return render(request, self.template_name, {'form': form})

        otp_code = _generate_otp()
        expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        cache.set(
            _otp_cache_key(email),
            {'code': otp_code, 'expires_at': expires_at, 'attempts': 0},
            OTP_EXPIRY_MINUTES * 60,
        )

        message = (
            f"Hi {user.get_full_name() or user.username},\n\n"
            f"Your HarmonyLeave password reset code is {otp_code}.\n"
            f"This code expires in {OTP_EXPIRY_MINUTES} minutes.\n\n"
            f"If you did not request this, you can ignore this email."
        )
        send_mail(
            subject='Password reset verification code',
            message=message,
            from_email=_get_from_email(),
            recipient_list=[email],
            fail_silently=True,
        )

        # Preserve the email for the next step and clear any previous verification
        request.session['password_reset_email'] = email
        request.session.pop('password_reset_email_verified', None)

        # When using console backend, surface the code to avoid digging through logs
        if 'console' in settings.EMAIL_BACKEND.lower():
            request.session['password_reset_otp_preview'] = otp_code

        messages.success(request, f'We sent a 6-digit code to {email}.')
        return redirect('password_reset_verify')


class OTPPasswordResetVerifyView(View):
    """
    Step 2: Verify the OTP the user received via email.
    """

    template_name = 'registration/password_reset_otp.html'

    def get(self, request):
        email = request.session.get('password_reset_email')
        if not email:
            messages.error(request, 'Enter your email to request a reset code.')
            return redirect('password_reset')

        otp_preview = request.session.pop('password_reset_otp_preview', None)
        form = OTPVerifyForm(initial={'email': email})
        return render(
            request,
            self.template_name,
            {'form': form, 'email': email, 'otp_preview': otp_preview},
        )

    def post(self, request):
        form = OTPVerifyForm(request.POST)
        email = request.session.get('password_reset_email')
        if not email:
            messages.error(request, 'Enter your email to request a reset code.')
            return redirect('password_reset')

        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'email': email})

        otp = form.cleaned_data['otp']
        cache_key = _otp_cache_key(email)
        data = cache.get(cache_key)

        if not data:
            form.add_error(None, 'The code has expired or is invalid. Request a new code.')
            return render(request, self.template_name, {'form': form, 'email': email})

        if timezone.now() > data['expires_at']:
            cache.delete(cache_key)
            form.add_error(None, 'The code has expired. Request a new code.')
            return render(request, self.template_name, {'form': form, 'email': email})

        attempts = data.get('attempts', 0)
        if attempts >= OTP_MAX_ATTEMPTS:
            cache.delete(cache_key)
            form.add_error(None, 'Too many invalid attempts. Request a new code.')
            return render(request, self.template_name, {'form': form, 'email': email})

        if otp != data['code']:
            attempts += 1
            data['attempts'] = attempts
            remaining_seconds = max(int((data['expires_at'] - timezone.now()).total_seconds()), 0)
            cache.set(cache_key, data, remaining_seconds)
            form.add_error('otp', f'Invalid code. {OTP_MAX_ATTEMPTS - attempts} attempt(s) left.')
            return render(request, self.template_name, {'form': form, 'email': email})

        # Success: mark email as verified for the password change step
        cache.delete(cache_key)
        request.session['password_reset_email_verified'] = email
        messages.success(request, 'Code verified. Set your new password below.')
        return redirect('password_reset_new_password')


class OTPPasswordResetNewPasswordView(View):
    """
    Step 3: Let the verified user set a new password.
    """

    template_name = 'registration/password_reset_confirm.html'

    def _get_user(self, email):
        return User.objects.filter(email__iexact=email, is_active=True).first()

    def get(self, request):
        email = request.session.get('password_reset_email_verified')
        if not email:
            messages.error(request, 'Verify the code sent to your email first.')
            return redirect('password_reset')

        user = self._get_user(email)
        if not user:
            messages.error(request, 'No active account found for that email.')
            return redirect('password_reset')

        form = CustomSetPasswordForm(user)
        return render(
            request,
            self.template_name,
            {'form': form, 'otp_flow': True, 'email': email},
        )

    def post(self, request):
        email = request.session.get('password_reset_email_verified')
        if not email:
            messages.error(request, 'Verify the code sent to your email first.')
            return redirect('password_reset')

        user = self._get_user(email)
        if not user:
            messages.error(request, 'No active account found for that email.')
            return redirect('password_reset')

        form = CustomSetPasswordForm(user, request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {'form': form, 'otp_flow': True, 'email': email},
            )

        form.save()
        request.session.pop('password_reset_email', None)
        request.session.pop('password_reset_email_verified', None)
        messages.success(request, 'Password updated successfully.')
        return redirect('password_reset_complete')


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    """
    Retain the token-based reset flow (used by admin-generated links) while
    applying the custom password rules.
    """

    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'

