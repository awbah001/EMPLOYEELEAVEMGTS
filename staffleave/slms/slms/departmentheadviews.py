from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, date, timedelta
from calendar import monthrange
from slmsapp.models import (
    CustomUser, Staff, Staff_Leave, Department, DepartmentHead, LeaveType, PublicHoliday, CalendarEvent
)
from .decorators import department_head_required


@login_required(login_url='/')
@department_head_required
def HOME(request):
    """Department Head Dashboard"""
    try:
        dept_head = DepartmentHead.objects.get(admin=request.user)
        department = dept_head.department
        
        # Get all staff in the department
        department_staff = Staff.objects.filter(department=department)
        
        # Get pending leave applications from department staff
        pending_leaves = Staff_Leave.objects.filter(
            staff_id__department=department,
            status=0
        ).order_by('-created_at')
        
        # Get approved leaves this month
        current_month = date.today().month
        current_year = date.today().year
        approved_this_month = Staff_Leave.objects.filter(
            staff_id__department=department,
            status=1,
            created_at__month=current_month,
            created_at__year=current_year
        ).count()
        # Rejected this month for department
        rejected_this_month = Staff_Leave.objects.filter(
            staff_id__department=department,
            status=2,
            created_at__month=current_month,
            created_at__year=current_year
        ).count()
        
        context = {
            'department': department,
            'department_staff_count': department_staff.count(),
            'pending_leaves': pending_leaves[:10],  # Latest 10
            'pending_count': pending_leaves.count(),
            'approved_this_month': approved_this_month,
            'rejected_this_month': rejected_this_month,
        }
        return render(request, 'departmenthead/home.html', context)
    except DepartmentHead.DoesNotExist:
        messages.error(request, 'Department Head profile not found.')
        return redirect('login')


@login_required(login_url='/')
@department_head_required
def REVIEW_LEAVE_APPLICATIONS(request):
    """View all leave applications from department staff"""
    try:
        dept_head = DepartmentHead.objects.get(admin=request.user)
        department = dept_head.department
        
        # Get all leave applications from department staff
        leave_applications = Staff_Leave.objects.filter(
            staff_id__department=department
        ).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            leave_applications = leave_applications.filter(status=int(status_filter))
        
        context = {
            'leave_applications': leave_applications,
            'department': department,
            'status_filter': status_filter,
        }
        return render(request, 'departmenthead/review_leaves.html', context)
    except DepartmentHead.DoesNotExist:
        messages.error(request, 'Department Head profile not found.')
        return redirect('login')


@login_required(login_url='/')
@department_head_required
def APPROVE_LEAVE(request, id):
    """Approve a leave application"""
    try:
        dept_head = DepartmentHead.objects.get(admin=request.user)
        leave = get_object_or_404(Staff_Leave, id=id)
        
        # Verify the leave belongs to staff in this department
        if leave.staff_id.department != dept_head.department:
            messages.error(request, 'You can only approve leaves from your department.')
            return redirect('dh_review_leaves')
        
        if leave.status != 0:
            messages.warning(request, 'This leave application has already been processed.')
            return redirect('dh_review_leaves')
        
        leave.status = 1
        leave.approved_by_department_head = request.user
        leave.save()
        
        # Update leave balance automatically
        from .leave_utils import update_leave_balance_on_approval
        if update_leave_balance_on_approval(leave):
            messages.success(request, f'Leave application from {leave.staff_id.admin.get_full_name()} has been approved and leave balance updated.')
        else:
            messages.success(request, f'Leave application from {leave.staff_id.admin.get_full_name()} has been approved.')
        
        return redirect('dh_review_leaves')
    except DepartmentHead.DoesNotExist:
        messages.error(request, 'Department Head profile not found.')
        return redirect('login')


@login_required(login_url='/')
@department_head_required
def REJECT_LEAVE(request, id):
    """Reject a leave application"""
    if request.method == 'POST':
        try:
            dept_head = DepartmentHead.objects.get(admin=request.user)
            leave = get_object_or_404(Staff_Leave, id=id)
            
            # Verify the leave belongs to staff in this department
            if leave.staff_id.department != dept_head.department:
                messages.error(request, 'You can only reject leaves from your department.')
                return redirect('dh_review_leaves')
            
            if leave.status != 0:
                messages.warning(request, 'This leave application has already been processed.')
                return redirect('dh_review_leaves')
            
            rejection_reason = request.POST.get('rejection_reason', '')
            leave.status = 2
            leave.rejection_reason = rejection_reason
            leave.save()
            messages.success(request, f'Leave application from {leave.staff_id.admin.get_full_name()} has been rejected.')
            return redirect('dh_review_leaves')
        except DepartmentHead.DoesNotExist:
            messages.error(request, 'Department Head profile not found.')
            return redirect('login')
    
    # GET request - show rejection form
    leave = get_object_or_404(Staff_Leave, id=id)
    context = {'leave': leave}
    return render(request, 'departmenthead/reject_leave.html', context)


@login_required(login_url='/')
@department_head_required
def DEPARTMENTAL_CALENDAR(request):
    """View departmental leave calendar"""
    try:
        dept_head = DepartmentHead.objects.get(admin=request.user)
        department = dept_head.department
        
        # Get ALL leaves (approved, pending, rejected) from department staff only
        department_leaves = Staff_Leave.objects.filter(
            staff_id__department=department
        ).order_by('from_date')
        
        # Get current month/year or from request
        year = int(request.GET.get('year', date.today().year))
        month = int(request.GET.get('month', date.today().month))
        
        # Filter leaves for the selected month
        month_leaves = department_leaves.filter(
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
            'department': department,
            'approved_leaves': month_leaves,
            'public_holidays': public_holidays,
            'calendar_events': calendar_events,
            'current_year': year,
            'current_month': month,
        }
        return render(request, 'departmenthead/calendar.html', context)
    except DepartmentHead.DoesNotExist:
        messages.error(request, 'Department Head profile not found.')
        return redirect('login')


@login_required(login_url='/')
@department_head_required
def MANAGE_TEAM_SCHEDULES(request):
    """Manage team schedules and view staff availability"""
    try:
        dept_head = DepartmentHead.objects.get(admin=request.user)
        department = dept_head.department
        
        # Get all staff in the department
        department_staff = Staff.objects.filter(department=department)
        
        # Get upcoming approved leaves
        today = date.today()
        upcoming_leaves = Staff_Leave.objects.filter(
            staff_id__department=department,
            status=1,
            from_date__gte=today
        ).order_by('from_date')
        
        context = {
            'department': department,
            'department_staff': department_staff,
            'upcoming_leaves': upcoming_leaves,
        }
        return render(request, 'departmenthead/team_schedules.html', context)
    except DepartmentHead.DoesNotExist:
        messages.error(request, 'Department Head profile not found.')
        return redirect('login')

