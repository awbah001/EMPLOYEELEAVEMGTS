from django.shortcuts import render, redirect, HttpResponse
from slmsapp.EmailBackEnd import EmailBackEnd
from django.contrib.auth import logout, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from slmsapp.models import CustomUser, Employee, Employee_Leave, LeaveType, LeaveBalance, PublicHoliday, CalendarEvent
from django.db.models import Q
from datetime import date, datetime, timedelta
from calendar import monthrange
from .decorators import employee_required
from .leave_utils import calculate_working_days, check_overlapping_leave
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/')
@employee_required
def HOME(request):
    """Employee Dashboard with leave history and calendar"""
    try:
        employee = Employee.objects.get(admin=request.user.id)
        
        # Get all leaves for this employee
        all_leaves = Employee_Leave.objects.filter(employee_id=employee.id).order_by('-created_at')
        
        # Get only the latest 5 for dashboard preview
        employee_leave_history = all_leaves[:5]

        # Counts for quick stats on dashboard
        total_applications = all_leaves.count()
        pending_count = all_leaves.filter(status=0).count()
        approved_count = all_leaves.filter(status=1).count()
        rejected_count = all_leaves.filter(status=2).count()
        
        # Get leave balances
        current_year = date.today().year
        leave_balances = LeaveBalance.objects.filter(
            employee=employee,
            year=current_year
        )
        
        context = {
            'employee': employee,
            'employee_leave_history': employee_leave_history,
            'leave_balances': leave_balances,
            'total_applications': total_applications,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
        }
        return render(request, 'staff/home.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error in HOME view for user {request.user.id}: {str(e)}', exc_info=True)
        messages.error(request, 'An error occurred while loading your dashboard.')
        return redirect('login')


@login_required(login_url='/')
@employee_required
def STAFF_APPLY_LEAVE(request):
    """Apply for leave form"""
    try:
        employee = Employee.objects.get(admin=request.user.id)
        leave_types = LeaveType.objects.filter(is_active=True)
        
        # Get leave balances for current year
        current_year = date.today().year
        leave_balances = LeaveBalance.objects.filter(
            employee=employee,
            year=current_year
        )
        
        # Check if user is currently on leave (has approved leave that includes today)
        today = date.today()
        current_leave = Employee_Leave.objects.filter(
            employee_id=employee,
            status=1,  # Approved
            from_date__lte=today,
            to_date__gte=today
        ).first()
        
        context = {
            'leave_types': leave_types,
            'leave_balances': leave_balances,
            'current_leave': current_leave,
            'is_on_leave': current_leave is not None,
        }
        return render(request, 'staff/apply_leave.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')


@login_required(login_url='/')
@employee_required
def STAFF_APPLY_LEAVE_SAVE(request):
    """Save leave application with validation"""
    if request.method == "POST":
        try:
            from datetime import date, datetime, timedelta
            from django.db.models import Q
            from slmsapp.models import LeaveBalance, PublicHoliday
            
            employee = Employee.objects.get(admin=request.user.id)
            
            # Check if user is currently on leave (has approved leave that includes today)
            today = date.today()
            current_leave = Employee_Leave.objects.filter(
                employee_id=employee,
                status=1,  # Approved
                from_date__lte=today,
                to_date__gte=today
            ).first()
            
            if current_leave:
                messages.error(request, f'You cannot apply for leave while you are currently on leave. Your current leave period is from {current_leave.from_date.strftime("%B %d, %Y")} to {current_leave.to_date.strftime("%B %d, %Y")}. Please wait until your current leave period ends.')
                return redirect('staff_apply_leave')
            
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
            working_days = calculate_working_days(from_date, to_date, employee)
            
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
                        employee=employee,
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
            overlapping_leave = check_overlapping_leave(employee, from_date, to_date)
            
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
            leave = Employee_Leave(
                employee_id=employee,
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
        except Employee.DoesNotExist:
            messages.error(request, 'Employee profile not found. Please contact administrator.')
            logger.error(f'Employee profile not found for user {request.user.id}')
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
@employee_required
def STAFF_LEAVE_VIEW(request):
    """View full leave history"""
    try:
        employee = Employee.objects.get(admin=request.user.id)
        
        # Get all leaves ordered by newest first
        all_leaves = Employee_Leave.objects.filter(employee_id=employee.id).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        employee_leave_history = all_leaves
        
        if status_filter:
            try:
                status_int = int(status_filter)
                employee_leave_history = employee_leave_history.filter(status=status_int)
            except (ValueError, TypeError):
                pass  # Invalid status filter, show all
        
        # Calculate status counts for all leaves (before filtering)
        total_count = all_leaves.count()
        pending_count = all_leaves.filter(status=0).count()
        approved_count = all_leaves.filter(status=1).count()
        rejected_count = all_leaves.filter(status=2).count()
        
        context = {
            'employee_leave_history': employee_leave_history,
            'status_filter': status_filter,
            'total_count': total_count,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
        }
        return render(request, 'staff/leave_history.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error in STAFF_LEAVE_VIEW for user {request.user.id}: {str(e)}', exc_info=True)
        messages.error(request, 'An error occurred while loading your leave history.')
        return redirect('staff_home')


@login_required(login_url='/')
@employee_required
def VIEW_LEAVE_BALANCE(request):
    """View leave balance"""
    try:
        employee = Employee.objects.get(admin=request.user.id)
        
        # Get current year or from request
        year = int(request.GET.get('year', date.today().year))
        
        # Get leave balances for the year
        leave_balances = LeaveBalance.objects.filter(
            employee=employee,
            year=year
        ).order_by('leave_type__name')
        
        # Calculate totals
        total_entitled = sum(balance.days_entitled for balance in leave_balances)
        total_used = sum(balance.days_used for balance in leave_balances)
        total_remaining = sum(balance.days_remaining for balance in leave_balances)
        
        context = {
            'employee': employee,
            'leave_balances': leave_balances,
            'current_year': year,
            'total_entitled': total_entitled,
            'total_used': total_used,
            'total_remaining': total_remaining,
        }
        return render(request, 'staff/leave_balance.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')


@login_required(login_url='/')
@employee_required
def TRACK_LEAVE_STATUS(request, leave_id):
    """Track specific leave application status"""
    try:
        employee = Employee.objects.get(admin=request.user.id)
        leave = Employee_Leave.objects.get(id=leave_id, employee_id=employee)
        
        context = {
            'leave': leave,
        }
        return render(request, 'staff/track_leave.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('login')
    except Employee_Leave.DoesNotExist:
        messages.error(request, 'Leave application not found.')
        return redirect('staff_leave_view')


@login_required(login_url='/')
@employee_required
def STAFF_CALENDAR(request):
    """View personal leave calendar"""
    # region agent log
    try:
        import json, time, os
        debugdir = os.path.dirname(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log')
        loginfo = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "H2",
            "location": "staffviews.py:292",
            "message": "FUNC_ENTRY and FS status",
            "data": {'cwd': os.getcwd(), 'debug_log_dir_exists': os.path.exists(debugdir), 'debug_log_path': r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\\.cursor\\debug.log', 'debug_log_parent': debugdir},
            "timestamp": int(time.time()*1000)
        }
        with open(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log', 'a') as f:
            f.write(json.dumps(loginfo) + "\n")
    except Exception as log_exc:
        pass
    # endregion
    try:
        # region agent log
        try:
            import json, time
            with open(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "H4",
                    "location": "staffviews.py:294",
                    "message": "STAFF_CALENDAR entry",
                    "data": {"user_id": getattr(request.user, 'id', None)},
                    "timestamp": int(time.time()*1000)
                }) + "\n")
        except Exception as log_exc:
            pass
        # endregion

        employee = Employee.objects.get(admin=request.user.id)
        # region agent log
        try:
            import json, time
            with open(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "H2",
                    "location": "staffviews.py:295",
                    "message": "Employee instance fetched",
                    "data": {"employee_id": getattr(employee, 'id', None)},
                    "timestamp": int(time.time()*1000)
                }) + "\n")
        except Exception as log_exc:
            pass
        # endregion
        
        # Get all leaves for this employee member
        all_leaves = Employee_Leave.objects.filter(
            employee_id=employee
        ).order_by('from_date')
        
        # Get current month/year or from request
        year = int(request.GET.get('year', date.today().year))
        month = int(request.GET.get('month', date.today().month))
        
        # Filter leaves for the selected month
        month_leaves = all_leaves.filter(
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
        # region agent log
        try:
            import json, time
            with open(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log', 'a') as f:
                f.write(json.dumps({
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "H1",
                    "location": "staffviews.py:319",
                    "message": "Query CalendarEvent.before",
                    "data": {"year": year, "month": month},
                    "timestamp": int(time.time()*1000)
                }) + "\n")
        except Exception as log_exc:
            pass
        # endregion
        try:
            calendar_events = CalendarEvent.objects.filter(
                event_date__year=year,
                event_date__month=month,
                is_active=True
            )
            # region agent log
            try:
                import json, time
                with open(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "H1",
                        "location": "staffviews.py:324",
                        "message": "CalendarEvent query SUCCESS",
                        "data": {"count": calendar_events.count()},
                        "timestamp": int(time.time()*1000)
                    }) + "\n")
            except Exception as log_exc:
                pass
            # endregion
        except Exception as e:
            # region agent log
            try:
                import json, time
                with open(r'c:\Users\DEVNET\Desktop\Employee-Leave-MS-Django-Python\.cursor\debug.log', 'a') as f:
                    f.write(json.dumps({
                        "sessionId": "debug-session",
                        "runId": "run1",
                        "hypothesisId": "H1",
                        "location": "staffviews.py:324",
                        "message": "CalendarEvent query FAILED",
                        "data": {"error": str(e)},
                        "timestamp": int(time.time()*1000)
                    }) + "\n")
            except Exception as log_exc:
                pass
            # endregion
            raise

        # Build a day-by-day calendar map for the selected month
        first_weekday = date(year, month, 1).weekday()  # Monday=0
        days_in_month = monthrange(year, month)[1]
        leave_by_date = {}
        for leave in month_leaves:
            current = leave.from_date
            while current <= leave.to_date:
                if current.year == year and current.month == month:
                    leave_by_date[current] = leave
                current += timedelta(days=1)
        
        # Map holidays by date
        holiday_by_date = {h.date: h for h in public_holidays}
        
        # Map events by date
        events_by_date = {}
        for event in calendar_events:
            if event.event_date not in events_by_date:
                events_by_date[event.event_date] = []
            events_by_date[event.event_date].append(event)

        calendar_days = []
        today = date.today()
        status_labels = {0: 'Pending', 1: 'Approved', 2: 'Rejected'}
        for day in range(1, days_in_month + 1):
            current_date = date(year, month, day)
            leave = leave_by_date.get(current_date)
            holiday = holiday_by_date.get(current_date)
            events = events_by_date.get(current_date, [])
            
            status = None
            status_label = None
            leave_name = None
            if leave:
                status = {0: 'pending', 1: 'approved', 2: 'rejected'}.get(leave.status, 'pending')
                status_label = status_labels.get(leave.status, 'Pending')
                leave_name = leave.leave_type_name or (leave.leave_type.name if leave.leave_type else 'Leave')

            calendar_days.append(
                {
                    'day': day,
                    'date': current_date,
                    'is_today': current_date == today,
                    'leave': leave,
                    'status': status,
                    'status_label': status_label,
                    'leave_name': leave_name,
                    'holiday': holiday,
                    'events': events,
                }
            )
        
        context = {
            'employee': employee,
            'all_leaves': month_leaves,
            'public_holidays': public_holidays,
            'calendar_events': calendar_events,
            'current_year': year,
            'current_month': month,
            'month_name': date(year, month, 1).strftime('%B'),
            'leading_blanks': range(first_weekday),
            'calendar_days': calendar_days,
        }
        return render(request, 'staff/calendar.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('staff_home')