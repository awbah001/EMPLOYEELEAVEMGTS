from slmsapp.models import Staff_Leave

def staff_leave_notifications(request):
    """
    Context processor to add staff_leave notifications to all templates
    """
    if request.user.is_authenticated and request.user.user_type == '1':
        staff_leave = Staff_Leave.objects.all()
        return {'staff_leave': staff_leave}
    return {'staff_leave': []}

