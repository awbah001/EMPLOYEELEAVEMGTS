"""
Utility functions for leave management
"""
from datetime import date, timedelta
from django.db.models import Q
from slmsapp.models import LeaveBalance, Staff_Leave, PublicHoliday


def calculate_working_days(from_date, to_date, staff=None):
    """
    Calculate working days between two dates, excluding weekends and public holidays
    
    Args:
        from_date: Start date
        to_date: End date
        staff: Staff object (optional, for department-specific holidays)
    
    Returns:
        int: Number of working days
    """
    if from_date > to_date:
        return 0
    
    working_days = 0
    current_date = from_date
    
    # Get public holidays in the date range
    holidays = PublicHoliday.objects.filter(
        date__gte=from_date,
        date__lte=to_date,
        is_active=True
    ).values_list('date', flat=True)
    
    while current_date <= to_date:
        # Check if not weekend (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            # Check if not a holiday
            if current_date not in holidays:
                working_days += 1
        current_date += timedelta(days=1)
    
    return working_days


def update_leave_balance_on_approval(leave):
    """
    Update leave balance when leave is approved
    
    Args:
        leave: Staff_Leave instance
    
    Returns:
        bool: True if balance was updated, False otherwise
    """
    if not leave.leave_type:
        return False
    
    # Calculate working days
    working_days = calculate_working_days(leave.from_date, leave.to_date, leave.staff_id)
    
    if working_days <= 0:
        return False
    
    # Get or create leave balance for current year
    current_year = date.today().year
    leave_balance, created = LeaveBalance.objects.get_or_create(
        staff=leave.staff_id,
        leave_type=leave.leave_type,
        year=current_year,
        defaults={
            'days_entitled': 0,
            'days_used': working_days,
            'days_remaining': 0 - working_days  # Will be recalculated in save()
        }
    )
    
    # Update days used
    if not created:
        leave_balance.days_used += working_days
        leave_balance.save()  # This will recalculate days_remaining
    
    return True


def revert_leave_balance_on_rejection(leave):
    """
    Revert leave balance when leave is rejected (if it was previously approved)
    
    Args:
        leave: Staff_Leave instance
    
    Returns:
        bool: True if balance was reverted, False otherwise
    """
    if not leave.leave_type:
        return False
    
    # Only revert if leave was previously approved (status was 1)
    if leave.status != 2:  # Only if currently rejected
        return False
    
    # Calculate working days
    working_days = calculate_working_days(leave.from_date, leave.to_date, leave.staff_id)
    
    if working_days <= 0:
        return False
    
    # Get leave balance for current year
    current_year = date.today().year
    try:
        leave_balance = LeaveBalance.objects.get(
            staff=leave.staff_id,
            leave_type=leave.leave_type,
            year=current_year
        )
        
        # Revert days used (only if it was previously approved)
        if leave_balance.days_used >= working_days:
            leave_balance.days_used -= working_days
            leave_balance.save()  # This will recalculate days_remaining
            return True
    except LeaveBalance.DoesNotExist:
        pass
    
    return False


def check_overlapping_leave(staff, from_date, to_date, exclude_leave_id=None):
    """
    Check if there are overlapping leave requests
    
    Args:
        staff: Staff instance
        from_date: Start date
        to_date: End date
        exclude_leave_id: Leave ID to exclude from check (for editing)
    
    Returns:
        QuerySet: Overlapping leaves
    """
    overlapping = Staff_Leave.objects.filter(
        staff_id=staff,
        status__in=[0, 1],  # Pending or Approved
    ).filter(
        Q(from_date__lte=to_date) & Q(to_date__gte=from_date)
    )
    
    if exclude_leave_id:
        overlapping = overlapping.exclude(id=exclude_leave_id)
    
    return overlapping

