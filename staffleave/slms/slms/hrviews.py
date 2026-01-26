from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, JsonResponse
from datetime import datetime, date, timedelta
from calendar import monthrange
import csv
from slmsapp.models import (
    CustomUser, Employee, Employee_Leave, Department, LeaveType, 
    LeaveEntitlement, LeaveBalance, PublicHoliday, SystemSettings, CalendarEvent
)
from .auth_utils import validate_password
from .decorators import hr_required, admin_or_hr_required, admin_required


@login_required(login_url='/')
@hr_required
def HOME(request):
    """HR Dashboard"""
    total_staff = Employee.objects.count()
    total_leaves = Employee_Leave.objects.count()
    pending_leaves = Employee_Leave.objects.filter(status=0).count()
    approved_leaves = Employee_Leave.objects.filter(status=1).count()
    rejected_leaves = Employee_Leave.objects.filter(status=2).count()
    
    # Get leaves pending HR approval
    hr_pending = Employee_Leave.objects.filter(
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
    employee_list = Employee.objects.all().select_related('admin', 'department')
    departments = Department.objects.all()
    
    context = {
        'employee_list': employee_list,
        'departments': departments,
    }
    return render(request, 'hr/manage_staff.html', context)


@login_required(login_url='/')
@admin_or_hr_required
def ADD_STAFF(request):
    """Add new staff member - HR can only create employees (user_type='2')"""
    if request.method == "POST":
        try:
            profile_pic = request.FILES.get('profile_pic')
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            address = request.POST.get('address', '').strip()
            gender = request.POST.get('gender', '')
            employee_type = request.POST.get('employee_type', '')
            department_id = request.POST.get('department')
            employee_id = request.POST.get('employee_id', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            date_of_joining = request.POST.get('date_of_joining')
            
            # HR can ONLY create employees (user_type='2')
            # Enforce this at backend regardless of form tampering
            user_role = '2'  # Always Employee for HR users

            # Validate required fields
            if not first_name or not last_name:
                messages.error(request, 'First name and last name are required.')
                return redirect('hr_add_staff')
            
            if not email:
                messages.error(request, 'Email is required.')
                return redirect('hr_add_staff')
            
            if not username:
                messages.error(request, 'Username is required.')
                return redirect('hr_add_staff')
            
            if not password:
                messages.error(request, 'Password is required.')
                return redirect('hr_add_staff')
            
            if not gender:
                messages.error(request, 'Gender is required.')
                return redirect('hr_add_staff')

            if CustomUser.objects.filter(email=email).exists():
                messages.warning(request, 'Email already exists')
                return redirect('hr_add_staff')
            
            if CustomUser.objects.filter(username=username).exists():
                messages.warning(request, 'Username already exists')
                return redirect('hr_add_staff')
            
            # Employee ID is now auto-generated, so we don't need to validate it
            # If provided, check for duplicates (though it will be auto-generated if not provided)
            if employee_id and Employee.objects.filter(employee_id=employee_id).exists():
                messages.warning(request, 'Employee ID already exists. Leave it blank to auto-generate.')
                return redirect('hr_add_staff')
            
            # Validate password
            ok, msg = validate_password(password)
            if not ok:
                messages.warning(request, msg)
                return redirect('hr_add_staff')
            
            # Create user as Employee (user_role will always be '2' for HR)
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                email=email,
                profile_pic=profile_pic,
                user_type=user_role,  # Always '2' (Employee)
                username=username
            )
            user.set_password(password)
            user.save()

            # Create employee profile (HR can ONLY create employees)
            department = None
            if department_id:
                try:
                    department = Department.objects.get(id=department_id)
                except Department.DoesNotExist:
                    messages.warning(request, 'Selected department not found. Employee created without department assignment.')
            
            employee = Employee(
                admin=user,
                address=address if address else None,
                gender=gender,
                employee_type=employee_type if employee_type else None,
                department=department,
                employee_id=employee_id if employee_id else None,  # Will be auto-generated if None
                phone_number=phone_number if phone_number else None,
                date_of_joining=date_of_joining if date_of_joining else None
            )
            employee.save()  # employee_id will be auto-generated in save() if not provided
            messages.success(request, 'Employee member added successfully.')
            
            return redirect('hr_manage_staff')
        
        except Exception as e:
            messages.error(request, f'An error occurred while adding staff: {str(e)}')
            import traceback
            print(f"Error in ADD_STAFF: {traceback.format_exc()}")
            return redirect('hr_add_staff')
    
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'hr/add_staff.html', context)


@login_required(login_url='/')
@admin_or_hr_required
def UPDATE_STAFF(request, id):
    """Update employee information"""
    employee = get_object_or_404(Employee, id=id)
    
    if request.method == "POST":
        user = employee.admin
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        employee_type = request.POST.get('employee_type', '')
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
        
        # Employee ID validation - if provided, check for duplicates
        # If not provided or empty, it will remain unchanged (or be auto-generated if currently None)
        if employee_id and employee_id.strip() and Employee.objects.filter(employee_id=employee_id).exclude(id=id).exists():
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
        
        employee.address = address
        employee.gender = gender
        if employee_type:
            employee.employee_type = employee_type
        if department_id:
            try:
                employee.department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                pass
        # Only update employee_id if a new value is provided
        # If empty/None, keep existing value (don't regenerate on update)
        if employee_id and employee_id.strip():
            employee.employee_id = employee_id
        elif not employee.employee_id:
            # Only auto-generate if employee_id is currently None/empty
            employee.employee_id = Employee.generate_employee_id()
        if phone_number:
            employee.phone_number = phone_number
        if date_of_joining:
            employee.date_of_joining = date_of_joining
        employee.save()
        
        messages.success(request, 'Employee details updated successfully')
        return redirect('hr_manage_staff')
    
    departments = Department.objects.all()
    context = {
        'employee': employee,
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
        employee_id = request.POST.get('employee_id')
        leave_type_id = request.POST.get('leave_type_id')
        entitlement_days = request.POST.get('entitlement_days', 0)
        year = request.POST.get('year', date.today().year)
        
        try:
            employee = Employee.objects.get(id=employee_id)
            leave_type = LeaveType.objects.get(id=leave_type_id)
            
            entitlement, created = LeaveEntitlement.objects.get_or_create(
                employee=employee,
                leave_type=leave_type,
                year=int(year),
                defaults={'days_entitled': float(entitlement_days)}
            )
            
            if not created:
                entitlement.days_entitled = float(entitlement_days)
                entitlement.save()
            
            # Update or create leave balance
            balance, created = LeaveBalance.objects.get_or_create(
                employee=employee,
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
    
    employee_list = Employee.objects.all().select_related('admin', 'department')
    leave_types = LeaveType.objects.filter(is_active=True)
    current_year = date.today().year
    
    # Get all entitlements with related data
    entitlements = LeaveEntitlement.objects.all().select_related(
        'employee__admin', 'leave_type'
    ).order_by('-year', 'employee__admin__first_name')
    
    # Add calculated fields for each entitlement
    for entitlement in entitlements:
        # Calculate used days from approved leaves
        approved_leaves = Employee_Leave.objects.filter(
            employee_id=entitlement.employee,
            leave_type=entitlement.leave_type,
            from_date__year=entitlement.year,
            status=1
        )
        used_days = sum([(leave.to_date - leave.from_date).days + 1 for leave in approved_leaves])
        
        entitlement.used_days = used_days
        entitlement.total_days = entitlement.days_entitled
        entitlement.remaining_days = entitlement.days_entitled - used_days
    
    context = {
        'employee_list': employee_list,
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
    pending_leaves = Employee_Leave.objects.filter(
        status=0
    ).select_related('employee_id__admin', 'employee_id__department', 'leave_type').order_by('-created_at')
    
    # Add calculated fields
    for leave in pending_leaves:
        leave.employee = leave.employee_id  # Alias for template compatibility
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
    approved_today = Employee_Leave.objects.filter(
        status=1,
        updated_at__date=date.today()
    ).count()
    rejected_today = Employee_Leave.objects.filter(
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
        leave = get_object_or_404(Employee_Leave, id=id)
        
        if leave.status == 2:
            messages.warning(request, 'Cannot approve a rejected leave application.')
            return redirect('hr_approve_leave')
        
        # Get approval comment if provided
        approval_comment = request.POST.get('approval_comment', '')
        
        leave.status = 1
        leave.approved_by_hr = request.user
        if approval_comment:
            leave.hr_approval_comment = approval_comment
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
        leave = get_object_or_404(Employee_Leave, id=id)
        rejection_reason = request.POST.get('rejection_reason', '')
        approval_comment = request.POST.get('approval_comment', '')
        leave.status = 2
        leave.rejection_reason = rejection_reason
        if approval_comment:
            leave.hr_approval_comment = approval_comment
        leave.save()
        messages.success(request, 'Leave application rejected.')
        return redirect('hr_approve_leave')
    
    leave = get_object_or_404(Employee_Leave, id=id)
    context = {'leave': leave}
    return render(request, 'hr/reject_leave.html', context)


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
def ANALYTICS_DASHBOARD(request):
    """Analytics Dashboard with KPIs and charts"""
    current_year = date.today().year
    current_date = date.today()
    
    # Get year from request, default to current year
    year = int(request.GET.get('year', current_year))
    
    # KPI Metrics
    total_employees = Employee.objects.count()
    total_leaves_applied = Employee_Leave.objects.filter(created_at__year=year).count()
    approved_leaves = Employee_Leave.objects.filter(status=1, created_at__year=year).count()
    pending_leaves = Employee_Leave.objects.filter(status=0, created_at__year=year).count()
    rejected_leaves = Employee_Leave.objects.filter(status=2, created_at__year=year).count()
    
    # Additional metrics
    from datetime import timedelta
    total_leave_days = sum([
        (leave.to_date - leave.from_date).days + 1 
        for leave in Employee_Leave.objects.filter(status=1, created_at__year=year)
    ])
    
    # Employees who took leave
    employees_with_leave = Employee_Leave.objects.filter(status=1, created_at__year=year).values('employee_id').distinct().count()
    
    # Average leaves per employee
    avg_leaves_per_employee = 0
    if employees_with_leave > 0:
        avg_leaves_per_employee = round(approved_leaves / employees_with_leave, 1)
    
    # Departments count
    total_departments = Department.objects.count()
    
    # Most common leave type
    most_common_leave_type = LeaveType.objects.annotate(
        count=Count('employee_leave')
    ).order_by('-count').first() if LeaveType.objects.exists() else None
    
    # Active leave types this year
    active_leave_types_year = LeaveType.objects.filter(
        employee_leave__created_at__year=year
    ).distinct().count()
    
    # Calculate percentages
    approval_rate = 0
    if total_leaves_applied > 0:
        approval_rate = round((approved_leaves / total_leaves_applied) * 100, 1)
    
    pending_percentage = 0
    if total_leaves_applied > 0:
        pending_percentage = round((pending_leaves / total_leaves_applied) * 100, 1)
    
    rejection_rate = 0
    if total_leaves_applied > 0:
        rejection_rate = round((rejected_leaves / total_leaves_applied) * 100, 1)
    
    # Utilization rate
    utilization_rate = 0
    if total_employees > 0:
        utilization_rate = round((employees_with_leave / total_employees) * 100, 1)
    
    # Monthly trend data for line chart
    monthly_data = []
    monthly_labels = []
    for month in range(1, 13):
        month_leaves = Employee_Leave.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count()
        monthly_data.append(month_leaves)
        month_name = date(year, month, 1).strftime('%b')
        monthly_labels.append(month_name)
    
    # Leave type distribution (pie chart)
    leave_types = LeaveType.objects.all()
    leave_type_data = []
    leave_type_labels = []
    leave_type_colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#06b6d4'
    ]
    
    for idx, lt in enumerate(leave_types):
        count = Employee_Leave.objects.filter(
            leave_type=lt,
            created_at__year=year
        ).count()
        if count > 0:
            leave_type_data.append(count)
            leave_type_labels.append(lt.name)
    
    # Department wise distribution (bar chart)
    departments = Department.objects.all()
    dept_data = []
    dept_labels = []
    dept_approved = []
    dept_pending = []
    dept_rejected = []
    
    for dept in departments:
        total = Employee_Leave.objects.filter(
            employee_id__department=dept,
            created_at__year=year
        ).count()
        approved = Employee_Leave.objects.filter(
            employee_id__department=dept,
            status=1,
            created_at__year=year
        ).count()
        pending = Employee_Leave.objects.filter(
            employee_id__department=dept,
            status=0,
            created_at__year=year
        ).count()
        rejected = Employee_Leave.objects.filter(
            employee_id__department=dept,
            status=2,
            created_at__year=year
        ).count()
        
        if total > 0:
            dept_data.append(total)
            dept_labels.append(dept.name[:15])  # Truncate long names
            dept_approved.append(approved)
            dept_pending.append(pending)
            dept_rejected.append(rejected)
    
    # Status distribution
    status_labels = ['Approved', 'Pending', 'Rejected']
    status_data = [approved_leaves, pending_leaves, rejected_leaves]
    status_colors = ['#10b981', '#f59e0b', '#ef4444']
    
    # Employee leave balance summary
    employees_on_leave_today = Employee_Leave.objects.filter(
        from_date__lte=current_date,
        to_date__gte=current_date,
        status=1
    ).count()
    
    # Top leave types
    top_leave_types = LeaveType.objects.annotate(
        count=Count('employee_leave')
    ).order_by('-count')[:5]
    
    context = {
        'current_year': current_year,
        'year': year,
        
        # KPIs
        'total_employees': total_employees,
        'total_leaves_applied': total_leaves_applied,
        'approved_leaves': approved_leaves,
        'pending_leaves': pending_leaves,
        'rejected_leaves': rejected_leaves,
        'approval_rate': approval_rate,
        'pending_percentage': pending_percentage,
        'rejection_rate': rejection_rate,
        'employees_on_leave_today': employees_on_leave_today,
        'total_leave_days': total_leave_days,
        'employees_with_leave': employees_with_leave,
        'avg_leaves_per_employee': avg_leaves_per_employee,
        'total_departments': total_departments,
        'most_common_leave_type': most_common_leave_type,
        'active_leave_types_year': active_leave_types_year,
        'utilization_rate': utilization_rate,
        
        # Chart data (JSON)
        'monthly_labels': monthly_labels,
        'monthly_data': monthly_data,
        'leave_type_labels': leave_type_labels,
        'leave_type_data': leave_type_data,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
        'dept_approved': dept_approved,
        'dept_pending': dept_pending,
        'dept_rejected': dept_rejected,
        'status_labels': status_labels,
        'status_data': status_data,
        'status_colors': status_colors,
        'top_leave_types': top_leave_types,
    }
    
    return render(request, 'hr/analytics_dashboard.html', context)


@login_required(login_url='/')
@admin_required
def ADMIN_ANALYTICS_DASHBOARD(request):
    """Admin Analytics Dashboard with KPIs and charts"""
    current_year = date.today().year
    current_date = date.today()
    
    # Get year from request, default to current year
    year = int(request.GET.get('year', current_year))
    
    # KPI Metrics
    # Count employees who are CustomUser type '2' (employees)
    total_employees = Employee.objects.filter(admin__user_type='2').count()
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()
    total_leaves_applied = Employee_Leave.objects.filter(created_at__year=year).count()
    approved_leaves = Employee_Leave.objects.filter(status=1, created_at__year=year).count()
    pending_leaves = Employee_Leave.objects.filter(status=0, created_at__year=year).count()
    rejected_leaves = Employee_Leave.objects.filter(status=2, created_at__year=year).count()
    
    # Additional admin metrics
    inactive_users = total_users - active_users
    
    # Total leave days
    total_leave_days = sum([
        (leave.to_date - leave.from_date).days + 1 
        for leave in Employee_Leave.objects.filter(status=1, created_at__year=year)
    ])
    
    # Employees with leave
    employees_with_leave = Employee_Leave.objects.filter(status=1, created_at__year=year).values('employee_id').distinct().count()
    
    # Average leaves per employee
    avg_leaves_per_employee = 0
    if employees_with_leave > 0:
        avg_leaves_per_employee = round(approved_leaves / employees_with_leave, 1)
    
    # Employee count by department
    dept_employee_counts = {}
    for dept in Department.objects.all():
        dept_employee_counts[dept.name] = Employee.objects.filter(department=dept).count()
    
    # User type counts
    admin_count = CustomUser.objects.filter(user_type='1').count()
    employee_count = CustomUser.objects.filter(user_type='2').count()
    dh_count = CustomUser.objects.filter(user_type='3').count()
    hr_count = CustomUser.objects.filter(user_type='4').count()
    
    # System settings info
    total_leave_types = LeaveType.objects.count()
    active_leave_types = LeaveType.objects.filter(is_active=True).count()
    total_holidays = PublicHoliday.objects.count()
    
    # Calculate percentages
    approval_rate = 0
    if total_leaves_applied > 0:
        approval_rate = round((approved_leaves / total_leaves_applied) * 100, 1)
    
    active_user_rate = 0
    if total_users > 0:
        active_user_rate = round((active_users / total_users) * 100, 1)
    
    # Utilization rate
    utilization_rate = 0
    if total_employees > 0:
        utilization_rate = round((employees_with_leave / total_employees) * 100, 1)
    
    # Monthly trend data for line chart
    monthly_data = []
    monthly_labels = []
    for month in range(1, 13):
        month_leaves = Employee_Leave.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).count()
        monthly_data.append(month_leaves)
        month_name = date(year, month, 1).strftime('%b')
        monthly_labels.append(month_name)
    
    # Leave type distribution (pie chart)
    leave_types = LeaveType.objects.all()
    leave_type_data = []
    leave_type_labels = []
    
    for lt in leave_types:
        count = Employee_Leave.objects.filter(
            leave_type=lt,
            created_at__year=year
        ).count()
        if count > 0:
            leave_type_data.append(count)
            leave_type_labels.append(lt.name)
    
    # Department wise distribution (bar chart)
    departments = Department.objects.all()
    dept_data = []
    dept_labels = []
    dept_approved = []
    dept_pending = []
    dept_rejected = []
    
    for dept in departments:
        total = Employee_Leave.objects.filter(
            employee_id__department=dept,
            created_at__year=year
        ).count()
        approved = Employee_Leave.objects.filter(
            employee_id__department=dept,
            status=1,
            created_at__year=year
        ).count()
        pending = Employee_Leave.objects.filter(
            employee_id__department=dept,
            status=0,
            created_at__year=year
        ).count()
        rejected = Employee_Leave.objects.filter(
            employee_id__department=dept,
            status=2,
            created_at__year=year
        ).count()
        
        if total > 0:
            dept_data.append(total)
            dept_labels.append(dept.name[:15])  # Truncate long names
            dept_approved.append(approved)
            dept_pending.append(pending)
            dept_rejected.append(rejected)
    
    # Status distribution
    status_labels = ['Approved', 'Pending', 'Rejected']
    status_data = [approved_leaves, pending_leaves, rejected_leaves]
    status_colors = ['#10b981', '#f59e0b', '#ef4444']
    
    # User type distribution
    from django.db.models import Q
    admin_count = CustomUser.objects.filter(user_type='1').count()
    employee_count = CustomUser.objects.filter(user_type='2').count()
    dh_count = CustomUser.objects.filter(user_type='3').count()
    hr_count = CustomUser.objects.filter(user_type='4').count()
    
    user_type_labels = ['Admin', 'Employee', 'Department Head', 'HR']
    user_type_data = [admin_count, employee_count, dh_count, hr_count]
    user_type_colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    
    context = {
        'current_year': current_year,
        'year': year,
        
        # KPIs - User Management
        'total_employees': total_employees,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_departments': total_departments,
        'active_user_rate': active_user_rate,
        
        # KPIs - Leave Management
        'total_leaves_applied': total_leaves_applied,
        'approved_leaves': approved_leaves,
        'pending_leaves': pending_leaves,
        'rejected_leaves': rejected_leaves,
        'approval_rate': approval_rate,
        'total_leave_days': total_leave_days,
        'employees_with_leave': employees_with_leave,
        'avg_leaves_per_employee': avg_leaves_per_employee,
        'utilization_rate': utilization_rate,
        
        # System Configuration
        'total_leave_types': total_leave_types,
        'active_leave_types': active_leave_types,
        'total_holidays': total_holidays,
        'admin_count': admin_count,
        'employee_count': employee_count,
        'dh_count': dh_count,
        'hr_count': hr_count,
        
        # Chart data (JSON)
        'monthly_labels': monthly_labels,
        'monthly_data': monthly_data,
        'leave_type_labels': leave_type_labels,
        'leave_type_data': leave_type_data,
        'dept_labels': dept_labels,
        'dept_data': dept_data,
        'dept_approved': dept_approved,
        'dept_pending': dept_pending,
        'dept_rejected': dept_rejected,
        'status_labels': status_labels,
        'status_data': status_data,
        'status_colors': status_colors,
        'user_type_labels': user_type_labels,
        'user_type_data': user_type_data,
        'user_type_colors': user_type_colors,
    }
    
    return render(request, 'admin/admin_analytics_dashboard.html', context)


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
    """Simple calendar widget for HR"""
    from datetime import date
    from calendar import monthrange
    
    # Get current month/year or from request
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Get public holidays for the month
    public_holidays = PublicHoliday.objects.filter(
        date__year=year,
        date__month=month,
        is_active=True
    )
    
    # Get calendar events for the month (all active events created by admins)
    calendar_events = CalendarEvent.objects.filter(
        event_date__year=year,
        event_date__month=month,
        is_active=True
    ).order_by('event_date', 'start_time')
    
    # Build simple calendar widget data
    first_weekday = date(year, month, 1).weekday()  # Monday=0
    days_in_month = monthrange(year, month)[1]
    
    # Map holidays by date
    holiday_by_date = {h.date: h for h in public_holidays}
    
    # Map events by date
    events_by_date = {}
    for event in calendar_events:
        if event.event_date not in events_by_date:
            events_by_date[event.event_date] = []
        events_by_date[event.event_date].append(event)
    
    # Build simple calendar days
    calendar_days = []
    today = date.today()
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        calendar_days.append({
            'day': day,
            'date': current_date,
            'is_today': current_date == today,
            'holiday': holiday_by_date.get(current_date),
            'events': events_by_date.get(current_date, []),
        })
    
    context = {
        'current_year': year,
        'current_month': month,
        'month_name': date(year, month, 1).strftime('%B'),
        'leading_blanks': range(first_weekday),
        'calendar_days': calendar_days,
        'public_holidays': public_holidays,
        'calendar_events': calendar_events,
    }
    return render(request, 'hr/calendar.html', context)

# SavedFilter Views
from slmsapp.models import SavedFilter
from django.http import JsonResponse
import json

@login_required(login_url='/')
def save_filter(request):
    """Save a filter combination"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            filter_name = data.get('name', '')
            filter_type = data.get('filter_type', 'custom')
            filter_params = data.get('params', {})
            
            if not filter_name:
                return JsonResponse({'success': False, 'message': 'Filter name is required'})
            
            # Check if filter with same name exists
            saved_filter, created = SavedFilter.objects.update_or_create(
                user=request.user,
                name=filter_name,
                defaults={
                    'filter_type': filter_type,
                    'filter_params': filter_params,
                }
            )
            
            message = 'Filter saved successfully' if created else 'Filter updated successfully'
            return JsonResponse({
                'success': True,
                'message': message,
                'filter_id': saved_filter.id,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='/')
def load_filter(request, filter_id):
    """Load a saved filter"""
    try:
        saved_filter = SavedFilter.objects.get(id=filter_id, user=request.user)
        return JsonResponse({
            'success': True,
            'name': saved_filter.name,
            'params': saved_filter.filter_params,
        })
    except SavedFilter.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Filter not found'})


@login_required(login_url='/')
def delete_filter(request, filter_id):
    """Delete a saved filter"""
    if request.method == 'POST':
        try:
            saved_filter = SavedFilter.objects.get(id=filter_id, user=request.user)
            saved_filter.delete()
            return JsonResponse({'success': True, 'message': 'Filter deleted successfully'})
        except SavedFilter.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Filter not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='/')
def list_saved_filters(request):
    """Get all saved filters for current user"""
    filter_type = request.GET.get('type', '')
    filters = SavedFilter.objects.filter(user=request.user)
    
    if filter_type:
        filters = filters.filter(filter_type=filter_type)
    
    return JsonResponse({
        'success': True,
        'filters': [
            {
                'id': f.id,
                'name': f.name,
                'filter_type': f.filter_type,
                'is_default': f.is_default,
                'params': f.filter_params,
            }
            for f in filters
        ]
    })