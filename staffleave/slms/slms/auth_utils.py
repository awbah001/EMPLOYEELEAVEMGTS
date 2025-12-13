from django.core.cache import cache
from slmsapp.models import SystemSettings
import re


def get_setting(key, default=None):
    s = SystemSettings.objects.filter(key=key).first()
    return s.value if s else default


def get_int_setting(key, default=0):
    val = get_setting(key, None)
    try:
        return int(val)
    except Exception:
        return default


def validate_password(password):
    """Validate password against system rules: minimum length and complexity.

    Returns: (is_valid: bool, message: str)
    """
    min_len = get_int_setting('password_min_length', 8)
    if not password or len(password) < min_len:
        return False, f'Password must be at least {min_len} characters long.'

    # complexity checks
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one digit.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, 'Password must contain at least one special character (e.g. !@#$%).'

    return True, 'OK'


def get_lockout_key(identifier):
    return f'slms_login_fail_{identifier}'


def get_lockout_info_key(identifier):
    return f'slms_login_locked_{identifier}'


def increment_failed_attempts(identifier, threshold, lock_minutes):
    key = get_lockout_key(identifier)
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=lock_minutes * 60)
    if count >= threshold:
        cache.set(get_lockout_info_key(identifier), True, timeout=lock_minutes * 60)
    return count


def is_locked_out(identifier):
    return cache.get(get_lockout_info_key(identifier), False)

