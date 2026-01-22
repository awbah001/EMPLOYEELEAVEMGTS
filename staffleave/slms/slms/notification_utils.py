"""
Utility functions for notification management
"""
from datetime import date
from slmsapp.models import Notification, Employee_Leave, CustomUser


def send_notification(sender, recipient, title, message, notification_type='info'):
    """
    Send a notification to a user
    
    Args:
        sender: CustomUser instance (sender)
        recipient: CustomUser instance (recipient)
        title: Notification title
        message: Notification message
        notification_type: Type of notification (info, warning, success, error, reminder)
    
    Returns:
        Notification: Created notification instance
    """
    notification = Notification.objects.create(
        sender=sender,
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        is_active=True
    )
    return notification


def notify_leave_ended(leave):
    """
    Send notification to employee when their leave has ended
    
    Args:
        leave: Employee_Leave instance that has ended
    
    Returns:
        Notification: Created notification instance or None
    """
    if not leave.employee_id or not leave.employee_id.admin:
        return None
    
    # Get system user as sender (or create a system user)
    system_user = CustomUser.objects.filter(user_type='1', is_superuser=True).first()
    if not system_user:
        # If no admin exists, skip notification
        return None
    
    title = f"Leave Ended - {leave.leave_type_name or 'Leave'}"
    message = f"Your leave from {leave.from_date.strftime('%B %d, %Y')} to {leave.to_date.strftime('%B %d, %Y')} has ended. Welcome back!"
    
    notification = send_notification(
        sender=system_user,
        recipient=leave.employee_id.admin,
        title=title,
        message=message,
        notification_type='info'
    )
    
    return notification


def check_and_notify_ended_leaves():
    """
    Check for leaves that have ended and send notifications to employees
    Notifications are only sent once per leave when it ends
    
    This should be called daily (e.g., via cron or scheduled task):
    python manage.py check_ended_leaves
    
    Returns:
        int: Number of notifications sent
    """
    from datetime import timedelta
    today = date.today()
    notifications_sent = 0
    
    # Find approved leaves that have ended but notification not yet sent
    # Includes leaves that ended today and all past dates
    ended_leaves = Employee_Leave.objects.filter(
        status=1,  # Approved leaves only
        to_date__lt=today,  # Leave end date has passed
        leave_end_notification_sent=False  # Notification not yet sent
    ).select_related('employee_id__admin', 'leave_type')
    
    for leave in ended_leaves:
        try:
            notification = notify_leave_ended(leave)
            if notification:
                # Mark notification as sent
                leave.leave_end_notification_sent = True
                leave.save(update_fields=['leave_end_notification_sent', 'updated_at'])
                notifications_sent += 1
                print(f"✓ Notification sent for leave {leave.id} ({leave.employee_id.admin.username})")
        except Exception as e:
            # Log error but continue processing other leaves
            print(f"✗ Error sending notification for leave {leave.id}: {str(e)}")
            continue
    
    return notifications_sent

