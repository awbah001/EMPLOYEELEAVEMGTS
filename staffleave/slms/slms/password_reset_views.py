from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form that uses email field for password reset
    """
    def get_users(self, email):
        """Return matching user(s) by email address."""
        active_users = User.objects.filter(
            email__iexact=email,
            is_active=True
        )
        return (u for u in active_users if u.has_usable_password())

class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    Custom password reset view that uses email instead of username
    """
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = '/password-reset/done/'

