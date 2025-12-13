from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, JsonResponse
from datetime import datetime, date, timedelta
from calendar import monthrange
import csv
from slmsapp.models import (
    CustomUser, Staff, Staff_Leave, Department, LeaveType, 
    LeaveEntitlement, LeaveBalance, PublicHoliday, SystemSettings, CalendarEvent
)
from .auth_utils import validate_password
from .decorators import hr_required, admin_or_hr_required


@login_required(login_url='/')
@hr_required
def HOME(request):
    """HR Dashboard"""
    total_staff = Staff.objects.count()
    total_leaves = Staff_Leave.objects.count()
    pending_leaves = Staff_Leave.objects.filter(status=0).count()
    approved_leaves = Staff_Leave.objects.filter(status=1).count()
    rejected_leaves = Staff_Leave.objects.filter(status=2).count()
    
    # Get leaves pending HR approval
    hr_pending = Staff_Leave.objects.filter(
        Q(status=0) | Q(status=1, approved_by_department_head__isnull=False, approved_by_hr__isnull=True)
    ).count()
    
    context = {
        'total_staff': total_staff,
        'total_leaves': total_leaves,
        'pending_leaves': pending_leaves,
        'approved_leaves': approved_leaves,
        'rejected_leaves': rejected_leaves,
        'hr_pending': hr_pending,
    }
    return render(request, 'hr/home.html', context)


@login_required(login_url='/')
@admin_or_hr_required
def MANAGE_STAFF(request):
    """Add and update staff information"""
    staff_list = Staff.objects.all().select_related('admin', 'department')
    departments = Department.objects.all()
    
    context = {
        'staff_list': staff_list,
        'departments': departments,
    }
    return render(request, 'hr/manage_staff.html', context)


@login_required(login_url='/')
@admin_or_hr_required
def ADD_STAFF(request):
    """Add new staff member"""
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        staff_type = request.POST.get('staff_type', '')
        department_id = request.POST.get('department')
        employee_id = request.POST.get('employee_id')
        phone_number = request.POST.get('phone_number')
        date_of_joining = request.POST.get('date_of_joining')
        user_role = request.POST.get('user_role', '2')  # Default to Staff

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            return redirect('hr_add_staff')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists')
            return redirect('hr_add_staff')
        
        if employee_id and Staff.objects.filter(employee_id=employee_id).exists():
            messages.warning(request, 'Employee ID already exists')
            return redirect('hr_add_staff')
        
        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            email=email,
            profile_pic=profile_pic,
            user_type=user_role,
            username=username
        )
        ok, msg = validate_password(password)
        if not ok:
            messages.warning(request, msg)
            return redirect('hr_add_staff')
        user.set_password(password)
        user.save()

        if user_role == '2':  # Staff
            department = None
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                except Department.DoesNotExist:
                    pass
            
            staff = Staff(
                admin=user,
                address=address,
                gender=gender,
                staff_type=staff_type if staff_type else None,
                department=department,
                employee_id=employee_id,
                phone_number=phone_number,
                date_of_joining=date_of_joining if date_of_joining else None
            )
            staff.save()
            messages.success(request, 'Staff member added successfully.')
        else:
            messages.success(request, 'User added successfully.')
        
        return redirect('hr_manage_staff')
    
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'hr/add_staff.html', context)


@login_required(login_url='/')
@admin_or_hr_required
def UPDATE_STAFF(request, id):
    """Update staff information"""
    staff = get_object_or_404(Staff, id=id)
    
    if request.method == "POST":
        user = staff.admin
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        staff_type = request.POST.get('staff_type', '')
        department_id = request.POST.get('department')
        employee_id = request.POST.get('employee_id')
        phone_number = request.POST.get('phone_number')
        date_of_joining = request.POST.get('date_of_joining')
        
        # Check for duplicate email/username
        if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
            messages.warning(request, 'Email already exists')
            return redirect('hr_update_staff', id=id)
        
        if CustomUser.objects.filter(username=username).exclude(id=user.id).exists():
            messages.warning(request, 'Username already exists')
            return redirect('hr_update_staff', id=id)
        
        if employee_id and Staff.objects.filter(employee_id=employee_id).exclude(id=id).exists():
            messages.warning(request, 'Employee ID already exists')
            return redirect('hr_update_staff', id=id)
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        if password:
            ok, msg = validate_password(password)
            if not ok:
                messages.warning(request, msg)
                return redirect('hr_update_staff', id=id)
            user.set_password(password)
        if profile_pic:
            user.profile_pic = profile_pic
        user.save()
        
        staff.address = address
        staff.gender = gender
        if staff_type:
            staff.staff_type = staff_type
        if department_id:
            try:
                staff.department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                pass
        if employee_id:
            staff.employee_id = employee_id
        if phone_number:
            staff.phone_number = phone_number
        if date_of_joining:
            staff.date_of_joining = date_of_joining
        staff.save()
        
        messages.success(request, 'Staff details updated successfully')
        return redirect('hr_manage_staff')
    
    departments = Department.objects.all()
    context = {
        'staff': staff,
        'departments': departments,
    }
    return render(request, 'hr/update_staff.html', context)


@login_required(login_url='/')
@hr_required
def MANAGE_LEAVE_TYPES(request):
    """Define and manage leave types"""
    leave_types = LeaveType.objects.all()
    
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        max_days = request.POST.get('max_days_per_year', 0)
        requires_approval = request.POST.get('requires_approval') == 'on'
        
        if LeaveType.objects.filter(name=name).exists():
            messages.warning(request, 'Leave type with this name already exists')
        else:
            LeaveType.objects.create(
                name=name,
                description=description,
                max_days_per_year=int(max_days) if max_days else 0,
                requires_approval=requires_approval
            )
            messages.success(request, 'Leave type added successfully')
        
        return redirect('hr_manage_leave_types')
    
    context = {'leave_types': leave_types}
    return render(request, 'hr/manage_leave_types.html', context)


@login_required(login_url='/')
@hr_required
def UPDATE_LEAVE_TYPE(request, id):
    """Update leave type"""
    leave_type = get_object_or_404(LeaveType, id=id)
    
    if request.method == "POST":
        leave_type.name = request.POST.get('name')
        leave_type.description = request.POST.get('description')
        leave_type.max_days_per_year = int(request.POST.get('max_days_per_year', 0))
        leave_type.requires_approval = request.POST.get('requires_approval') == 'on'
        leave_type.is_active = request.POST.get('is_active') == 'on'
        leave_type.save()
        messages.success(request, 'Leave type updated successfully')
        return redirect('hr_manage_leave_types')
    
    context = {'leave_type': leave_type}
    return render(request, 'hr/update_leave_type.html', context)


@login_required(login_url='/')
@hr_required
def SET_LEAVE_ENTITLEMENTS(request):
    """Set leave entitlements for staff"""
    if request.method == "POST":
        staff_id = request.POST.get('staff_id')
        leave_type_id = request.POST.get('leave_type_id')
        entitlement_days = request.POST.get('entitlement_days', 0)
        year = request.POST.get('year', date.today().year)
        
        try:
            staff = Staff.objects.get(id=staff_id)
            leave_type = LeaveType.objects.get(id=leave_type_id)
            
            entitlement, created = LeaveEntitlement.objects.get_or_create(
                staff=staff,
                leave_type=leave_type,
                year=int(year),
                defaults={'days_entitled': float(entitlement_days)}
            )
            
            if not created:
                entitlement.days_entitled = float(entitlement_days)
                entitlement.save()
            
            # Update or create leave balance
            balance, created = LeaveBalance.objects.get_or_create(
                staff=staff,
                leave_type=leave_type,
                year=int(year),
                defaults={'days_entitled': float(entitlement_days), 'days_used': 0}
            )
            
            if not created:
                balance.days_entitled = float(entitlement_days)
                balance.save()
            
            messages.success(request, 'Leave entitlement set successfully')
        except Exception as e:
            messages.error(request, f'Error setting entitlement: {str(e)}')
        
        return redirect('hr_set_entitlements')
    
    staff_list = Staff.objects.all().select_related('admin', 'department')
    leave_types = LeaveType.objects.filter(is_active=True)
    current_year = date.today().year
    
    # Get all entitlements with related data
    entitlements = LeaveEntitlement.objects.all().select_related(
        'staff__admin', 'leave_type'
    ).order_by('-year', 'staff__admin__first_name')
    
    # Add calculated fields for each entitlement
    for entitlement in entitlements:
        # Calculate used days from approved leaves
        approved_leaves = Staff_Leave.objects.filter(
            staff_id=entitlement.staff,
            leave_type=entitlement.leave_type,
            from_date__year=entitlement.year,
            status=1
        )
        used_days = sum([(leave.to_date - leave.from_date).days + 1 for leave in approved_leaves])
        
        entitlement.used_days = used_days
        entitlement.total_days = entitlement.days_entitled
        entitlement.remaining_days = entitlement.days_entitled - used_days
    
    context = {
        'staff_list': staff_list,
        'leave_types': leave_types,
        'current_year': current_year,
        'entitlements': entitlements,
    }
    return render(request, 'hr/set_entitlements.html', context)


@login_required(login_url='/')
@hr_required
def APPROVE_OVERRIDE_LEAVE(request):
    """Manually approve or override leave applications"""
    # Get pending leaves
    pending_leaves = Staff_Leave.objects.filter(
        status=0
    ).select_related('staff_id__admin', 'staff_id__department', 'leave_type').order_by('-created_at')
    
    # Add calculated fields
    for leave in pending_leaves:
        leave.staff = leave.staff_id  # Alias for template compatibility
        leave.start_date = leave.from_date
        leave.end_date = leave.to_date
        leave.reason = leave.message
        # Calculate number of days
        delta = leave.to_date - leave.from_date
        leave.number_of_days = delta.days + 1
        # Determine supervisor status
        if leave.approved_by_department_head:
            leave.supervisor_status = 'approved'
        else:
            leave.supervisor_status = 'pending'
    
    # Statistics
    pending_count = pending_leaves.count()
    approved_today = Staff_Leave.objects.filter(
        status=1,
        updated_at__date=date.today()
    ).count()
    rejected_today = Staff_Leave.objects.filter(
        status=2,
        updated_at__date=date.today()
    ).count()
    
    context = {
        'pending_leaves': pending_leaves,
        'pending_count': pending_count,
        'approved_today': approved_today,
        'rejected_today': rejected_today,
    }
    return render(request, 'hr/approve_leave.html', context)


@login_required(login_url='/')
@hr_required
def HR_APPROVE_LEAVE(request, id):
    """HR approve leave"""
    if request.method == 'POST':
        leave = get_object_or_404(Staff_Leave, id=id)
        
        if leave.status == 2:
            messages.warning(request, 'Cannot approve a rejected leave application.')
            return redirect('hr_approve_leave')
        
        leave.status = 1
        leave.approved_by_hr = request.user
        leave.save()
        
        # Update leave balance automatically
        from .leave_utils import update_leave_balance_on_approval
        if update_leave_balance_on_approval(leave):
            messages.success(request, 'Leave application approved successfully and leave balance updated.')
        else:
            messages.success(request, 'Leave application approved successfully.')
        
        return redirect('hr_approve_leave')
    
    return redirect('hr_approve_leave')


@login_required(login_url='/')
@hr_required
def HR_REJECT_LEAVE(request, id):
    """HR reject leave"""
    if request.method == 'POST':
        leave = get_object_or_404(Staff_Leave, id=id)
        rejection_reason = request.POST.get('rejection_reason', '')
        leave.status = 2
        leave.rejection_reason = rejection_reason
        leave.save()
        messages.success(request, 'Leave application rejected.')
        return redirect('hr_approve_leave')
    
    leave = get_object_or_404(Staff_Leave, id=id)
    context = {'leave': leave}
    return render(request, 'hr/reject_leave.html', context)


@login_required(login_url='/')
@hr_required
def GENERATE_REPORTS(request):
    """Generate various reports"""
    report_type = request.GET.get('type', 'summary')
    year = int(request.GET.get('year', date.today().year))
    
    # Base context with common data
    current_year = date.today().year
    departments = Department.objects.all()
    
    # Overall statistics
    total_applications = Staff_Leave.objects.count()
    approved_applications = Staff_Leave.objects.filter(status=1).count()
    pending_applications = Staff_Leave.objects.filter(status=0).count()
    rejected_applications = Staff_Leave.objects.filter(status=2).count()
    
    context = {
        'report_type': report_type,
        'year': year,
        'current_year': current_year,
        'departments': departments,
        'total_applications': total_applications,
        'approved_applications': approved_applications,
        'pending_applications': pending_applications,
        'rejected_applications': rejected_applications,
    }
    
    if report_type == 'summary':
        # Summary report
        total_staff = Staff.objects.count()
        total_leaves = Staff_Leave.objects.filter(created_at__year=year).count()
        approved = Staff_Leave.objects.filter(status=1, created_at__year=year).count()
        rejected = Staff_Leave.objects.filter(status=2, created_at__year=year).count()
        pending = Staff_Leave.objects.filter(status=0, created_at__year=year).count()
        
        context.update({
            'total_staff': total_staff,
            'total_leaves': total_leaves,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
        })
    elif report_type == 'department':
        # Department-wise report
        dept_stats = []
        for dept in departments:
            dept_leaves = Staff_Leave.objects.filter(
                staff_id__department=dept,
                created_at__year=year
            )
            dept_stats.append({
                'department': dept,
                'total': dept_leaves.count(),
                'approved': dept_leaves.filter(status=1).count(),
                'rejected': dept_leaves.filter(status=2).count(),
                'pending': dept_leaves.filter(status=0).count(),
            })
        context['dept_stats'] = dept_stats
    elif report_type == 'leave_type':
        # Leave type-wise report
        leave_types = LeaveType.objects.all()
        type_stats = []
        for lt in leave_types:
            type_leaves = Staff_Leave.objects.filter(
                leave_type=lt,
                created_at__year=year
            )
            type_stats.append({
                'leave_type': lt,
                'total': type_leaves.count(),
                'approved': type_leaves.filter(status=1).count(),
            })
        context['type_stats'] = type_stats
    
    return render(request, 'hr/reports.html', context)


@login_required(login_url='/')
@hr_required
def EXPORT_REPORT(request):
    """Export report as CSV"""
    report_type = request.GET.get('type', 'summary')
    year = int(request.GET.get('year', date.today().year))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="leave_report_{report_type}_{year}.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'summary':
        writer.writerow(['Report Type', 'Year', 'Total Staff', 'Total Leaves', 'Approved', 'Rejected', 'Pending'])
        total_staff = Staff.objects.count()
        total_leaves = Staff_Leave.objects.filter(created_at__year=year).count()
        approved = Staff_Leave.objects.filter(status=1, created_at__year=year).count()
        rejected = Staff_Leave.objects.filter(status=2, created_at__year=year).count()
        pending = Staff_Leave.objects.filter(status=0, created_at__year=year).count()
        writer.writerow(['Summary', year, total_staff, total_leaves, approved, rejected, pending])
    
    return response


@login_required(login_url='/')
@hr_required
def MANAGE_PUBLIC_HOLIDAYS(request):
    """Manage public holidays and academic breaks"""
    if request.method == "POST":
        name = request.POST.get('name')
        holiday_date = request.POST.get('date')
        description = request.POST.get('description', '')
        is_recurring = request.POST.get('is_recurring') == 'on'
        
        if PublicHoliday.objects.filter(name=name, date=holiday_date).exists():
            messages.warning(request, 'This holiday already exists')
        else:
            PublicHoliday.objects.create(
                name=name,
                date=holiday_date,
                description=description,
                is_recurring=is_recurring
            )
            messages.success(request, 'Public holiday added successfully')
        
        return redirect('hr_manage_holidays')
    
    current_year = date.today().year
    holidays = PublicHoliday.objects.all().order_by('date')
    
    # Statistics
    total_holidays = holidays.count()
    upcoming_holidays = holidays.filter(date__gte=date.today()).count()
    recurring_holidays = holidays.filter(is_recurring=True).count()
    
    context = {
        'holidays': holidays,
        'current_year': current_year,
        'total_holidays': total_holidays,
        'upcoming_holidays': upcoming_holidays,
        'recurring_holidays': recurring_holidays,
    }
    return render(request, 'hr/manage_holidays.html', context)


@login_required(login_url='/')
@hr_required
def UPDATE_HOLIDAY(request, id):
    """Update public holiday"""
    holiday = get_object_or_404(PublicHoliday, id=id)
    
    if request.method == "POST":
        holiday.name = request.POST.get('name')
        holiday.date = request.POST.get('date')
        holiday.description = request.POST.get('description', '')
        holiday.is_recurring = request.POST.get('is_recurring') == 'on'
        holiday.save()
        messages.success(request, 'Holiday updated successfully')
        return redirect('hr_manage_holidays')
    
    context = {'holiday': holiday}
    return render(request, 'hr/update_holiday.html', context)


@login_required(login_url='/')
@hr_required
def DELETE_HOLIDAY(request, id):
    """Delete public holiday"""
    if request.method == 'POST':
        holiday = get_object_or_404(PublicHoliday, id=id)
        holiday.delete()
        messages.success(request, 'Holiday deleted successfully')
    return redirect('hr_manage_holidays')


@login_required(login_url='/')
@hr_required
def DELETE_ENTITLEMENT(request, id):
    """Delete leave entitlement"""
    if request.method == 'POST':
        entitlement = get_object_or_404(LeaveEntitlement, id=id)
        entitlement.delete()
        messages.success(request, 'Leave entitlement deleted successfully')
    return redirect('hr_set_entitlements')


@login_required(login_url='/')
@hr_required
def HR_CALENDAR(request):
    """View all leaves calendar for HR"""
    # Get all approved leaves across all departments
    approved_leaves = Staff_Leave.objects.filter(
        status=1
    ).order_by('from_date')
    
    # Get current month/year or from request
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Filter leaves for the selected month
    month_leaves = approved_leaves.filter(
        from_date__year=year,
        from_date__month=month
    )
    
    # Get public holidays for the month
    public_holidays = PublicHoliday.objects.filter(
        date__year=year,
        date__month=month,
        is_active=True
    )
    
    # Get calendar events for the month
    calendar_events = CalendarEvent.objects.filter(
        event_date__year=year,
        event_date__month=month,
        is_active=True
    )
    
    context = {
        'approved_leaves': month_leaves,
        'public_holidays': public_holidays,
        'calendar_events': calendar_events,
        'current_year': year,
        'current_month': month,
    }
    return render(request, 'hr/calendar.html', context)
