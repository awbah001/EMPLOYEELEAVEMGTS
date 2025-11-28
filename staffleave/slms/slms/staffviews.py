from django.shortcuts import render, redirect, HttpResponse
from slmsapp.EmailBackEnd import EmailBackEnd
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from slmsapp.models import CustomUser, Staff, Staff_Leave, LeaveType, LeaveBalance, PublicHoliday
from django.db.models import Q
from datetime import date, datetime, timedelta
from .decorators import staff_required
from .leave_utils import calculate_working_days, check_overlapping_leave
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/')
@staff_required
def HOME(request):
    """Staff Dashboard with leave history"""
    try:
        staff = Staff.objects.get(admin=request.user.id)
        staff_leave_history = Staff_Leave.objects.filter(staff_id=staff.id).order_by('-created_at')[:5]
        
        # Get leave balances
        current_year = date.today().year
        leave_balances = LeaveBalance.objects.filter(
            staff=staff,
            year=current_year
        )
        
        context = {
            'staff': staff,
            'staff_leave_history': staff_leave_history,
            'leave_balances': leave_balances,
        }
        return render(request, 'staff/home.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('login')


@login_required(login_url='/')
@staff_required
def STAFF_APPLY_LEAVE(request):
    """Apply for leave form"""
    try:
        staff = Staff.objects.get(admin=request.user.id)
        leave_types = LeaveType.objects.filter(is_active=True)
        
        # Get leave balances for current year
        current_year = date.today().year
        leave_balances = LeaveBalance.objects.filter(
            staff=staff,
            year=current_year
        )
        
        context = {
            'leave_types': leave_types,
            'leave_balances': leave_balances,
        }
        return render(request, 'staff/apply_leave.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('login')


@login_required(login_url='/')
@staff_required
def STAFF_APPLY_LEAVE_SAVE(request):
    """Save leave application with validation"""
    if request.method == "POST":
        try:
            from datetime import date, datetime, timedelta
            from django.db.models import Q
            from slmsapp.models import LeaveBalance, PublicHoliday
            
            staff = Staff.objects.get(admin=request.user.id)
            leave_type_id = request.POST.get('leave_type')
            from_date_str = request.POST.get('from_date')
            to_date_str = request.POST.get('to_date')
            message = request.POST.get('message')
            supporting_document = request.FILES.get('supporting_document')

            # Validate dates
            try:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                messages.error(request, 'Invalid date format. Please select valid dates.')
                return redirect('staff_apply_leave')
            
            # Validate from_date is not in the past
            if from_date < date.today():
                messages.error(request, 'Leave start date cannot be in the past. Please select a future date.')
                return redirect('staff_apply_leave')
            
            # Validate to_date is after from_date
            if to_date < from_date:
                messages.error(request, 'Leave end date must be after or equal to the start date.')
                return redirect('staff_apply_leave')
            
            # Calculate number of working days (excluding weekends and public holidays)
            working_days = calculate_working_days(from_date, to_date, staff)
            
            # Get leave type
            leave_type = None
            leave_type_name = ''
            if leave_type_id:
                try:
                    # Try to convert to integer if it's a string
                    if isinstance(leave_type_id, str) and not leave_type_id.isdigit():
                        # If it's not a digit, it might be a name - try to find by name
                        leave_type = LeaveType.objects.get(name=leave_type_id, is_active=True)
                        leave_type_name = leave_type.name
                    else:
                        # It's an ID - get by ID
                        leave_type = LeaveType.objects.get(id=int(leave_type_id))
                        leave_type_name = leave_type.name
                except (LeaveType.DoesNotExist, ValueError) as e:
                    # If leave type not found, use the provided value as name (for backward compatibility)
                    leave_type_name = str(leave_type_id) if leave_type_id else 'Other'
                    messages.warning(request, f'Leave type not found in system. Using "{leave_type_name}" as leave type name.')
            
            # Check leave balance if leave type is specified
            if leave_type:
                current_year = date.today().year
                try:
                    leave_balance = LeaveBalance.objects.get(
                        staff=staff,
                        leave_type=leave_type,
                        year=current_year
                    )
                    
                    # Check if sufficient balance
                    if leave_balance.days_remaining < working_days:
                        messages.error(
                            request, 
                            f'Insufficient leave balance. You have {leave_balance.days_remaining} days remaining, but requested {working_days} days.'
                        )
                        return redirect('staff_apply_leave')
                except LeaveBalance.DoesNotExist:
                    messages.warning(
                        request, 
                        f'No leave balance found for {leave_type_name}. Leave application submitted, but approval may require HR setup of entitlements.'
                    )
            
            # Check for overlapping leave requests
            overlapping_leave = check_overlapping_leave(staff, from_date, to_date)
            
            if overlapping_leave.exists():
                messages.error(
                    request, 
                    f'You already have a leave request for these dates. Please check your leave history.'
                )
                return redirect('staff_apply_leave')

            # Validate file if uploaded
            if supporting_document:
                # Check file size (5MB max)
                if supporting_document.size > 5 * 1024 * 1024:
                    messages.error(request, 'File size exceeds 5MB limit. Please upload a smaller file.')
                    return redirect('staff_apply_leave')
                
                # Check file extension
                allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
                file_ext = supporting_document.name.lower().split('.')[-1]
                if f'.{file_ext}' not in allowed_extensions:
                    messages.error(request, 'Invalid file type. Only PDF, DOC, DOCX, JPG, and PNG files are allowed.')
                    return redirect('staff_apply_leave')

            # Create leave application
            leave = Staff_Leave(
                staff_id=staff,
                leave_type=leave_type,
                leave_type_name=leave_type_name,
                from_date=from_date,
                to_date=to_date,
                message=message,
                supporting_document=supporting_document,
            )
            leave.save()
            messages.success(request, f'Leave application submitted successfully for {working_days} working day(s).')
            return redirect('staff_apply_leave')
        except Staff.DoesNotExist:
            messages.error(request, 'Staff profile not found. Please contact administrator.')
            logger.error(f'Staff profile not found for user {request.user.id}')
            return redirect('login')
        except ValueError as e:
            messages.error(request, f'Invalid input: {str(e)}. Please check your dates and try again.')
            logger.warning(f'Validation error for user {request.user.id}: {str(e)}')
            return redirect('staff_apply_leave')
        except Exception as e:
            messages.error(request, 'An unexpected error occurred while submitting your leave application. Please try again or contact support.')
            logger.error(f'Error submitting leave for user {request.user.id}: {str(e)}', exc_info=True)
            return redirect('staff_apply_leave')
    
    return redirect('staff_apply_leave')


@login_required(login_url='/')
@staff_required
def STAFF_LEAVE_VIEW(request):
    """View full leave history"""
    try:
        staff = Staff.objects.get(admin=request.user.id)
        staff_leave_history = Staff_Leave.objects.filter(staff_id=staff.id).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            staff_leave_history = staff_leave_history.filter(status=int(status_filter))
        
        context = {
            'staff_leave_history': staff_leave_history,
            'status_filter': status_filter,
        }
        return render(request, 'staff/leave_history.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('login')


@login_required(login_url='/')
@staff_required
def VIEW_LEAVE_BALANCE(request):
    """View leave balance"""
    try:
        staff = Staff.objects.get(admin=request.user.id)
        
        # Get current year or from request
        year = int(request.GET.get('year', date.today().year))
        
        # Get leave balances for the year
        leave_balances = LeaveBalance.objects.filter(
            staff=staff,
            year=year
        ).order_by('leave_type__name')
        
        # Calculate totals
        total_entitled = sum(balance.days_entitled for balance in leave_balances)
        total_used = sum(balance.days_used for balance in leave_balances)
        total_remaining = sum(balance.days_remaining for balance in leave_balances)
        
        context = {
            'staff': staff,
            'leave_balances': leave_balances,
            'current_year': year,
            'total_entitled': total_entitled,
            'total_used': total_used,
            'total_remaining': total_remaining,
        }
        return render(request, 'staff/leave_balance.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('login')


@login_required(login_url='/')
@staff_required
def TRACK_LEAVE_STATUS(request, leave_id):
    """Track specific leave application status"""
    try:
        staff = Staff.objects.get(admin=request.user.id)
        leave = Staff_Leave.objects.get(id=leave_id, staff_id=staff)
        
        context = {
            'leave': leave,
        }
        return render(request, 'staff/track_leave.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return redirect('login')
    except Staff_Leave.DoesNotExist:
        messages.error(request, 'Leave application not found.')
        return redirect('staff_leave_view')