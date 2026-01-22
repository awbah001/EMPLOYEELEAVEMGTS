from slmsapp.models import Employee_Leave

def employee_leave_notifications(request):
    """
    Context processor to add employee_leave notifications to all templates
    """
    if request.user.is_authenticated and request.user.user_type == '1':
        employee_leave = Employee_Leave.objects.all()
        return {'employee_leave': employee_leave}
    return {'employee_leave': []}

