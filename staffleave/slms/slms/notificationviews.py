from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from slmsapp.models import Notification, CustomUser
from slmsapp.forms import NotificationForm, BulkNotificationForm
from .decorators import admin_required, hr_required, department_head_required, role_required
import json


@login_required(login_url='/')
@role_required('1', '3', '4')  # Admin, Department Head, HR
def send_notification(request):
    """View for sending a single notification - Available to Admin, HR, and Department Head"""
    if request.method == 'POST':
        form = NotificationForm(request.POST, sender=request.user)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user
            notification.save()
            messages.success(request, f'Notification sent successfully to {notification.recipient.username}')
            return redirect('notification_sent_list')
    else:
        form = NotificationForm(sender=request.user)

    context = {
        'form': form,
        'title': 'Send Notification',
        'submit_button': 'Send Notification'
    }
    return render(request, 'notification/send_notification.html', context)


@login_required(login_url='/')
@role_required('1', '3', '4')  # Admin, Department Head, HR
def send_bulk_notification(request):
    """View for sending bulk notifications to multiple recipients - Available to Admin, HR, and Department Head"""
    if request.method == 'POST':
        form = BulkNotificationForm(request.POST, sender=request.user)
        if form.is_valid():
            recipients = form.cleaned_data['recipients']
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            notification_type = form.cleaned_data['notification_type']

            # Create notifications for each recipient
            notifications_created = 0
            for recipient in recipients:
                Notification.objects.create(
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    sender=request.user,
                    recipient=recipient
                )
                notifications_created += 1

            messages.success(request, f'Successfully sent {notifications_created} notifications')
            return redirect('notification_sent_list')
    else:
        form = BulkNotificationForm(sender=request.user)

    context = {
        'form': form,
        'title': 'Send Bulk Notification',
        'submit_button': 'Send to All Selected'
    }
    return render(request, 'notification/send_bulk_notification.html', context)


@login_required(login_url='/')
def notification_list(request):
    """View to display received notifications"""
    # Get filter parameters
    filter_type = request.GET.get('type', 'all')
    is_read = request.GET.get('read', None)

    # Base queryset
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender')

    # Apply filters
    if filter_type != 'all':
        notifications = notifications.filter(notification_type=filter_type)

    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        notifications = notifications.filter(is_read=is_read_bool)

    # Pagination
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page = request.GET.get('page')

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    # Count for badges
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    # Type counts
    type_counts = notifications.aggregate(
        info_count=Count('id', filter=Q(notification_type='info')),
        warning_count=Count('id', filter=Q(notification_type='warning')),
        success_count=Count('id', filter=Q(notification_type='success')),
        error_count=Count('id', filter=Q(notification_type='error')),
        reminder_count=Count('id', filter=Q(notification_type='reminder')),
    )

    context = {
        'notifications': notifications_page,
        'unread_count': unread_count,
        'type_counts': type_counts,
        'filter_type': filter_type,
        'filter_read': is_read,
        'title': 'My Notifications'
    }
    return render(request, 'notification/notification_list.html', context)


@login_required(login_url='/')
def sent_notifications(request):
    """View to display sent notifications"""
    # Get filter parameters
    filter_type = request.GET.get('type', 'all')

    # Base queryset
    notifications = Notification.objects.filter(
        sender=request.user
    ).select_related('recipient')

    # Apply filters
    if filter_type != 'all':
        notifications = notifications.filter(notification_type=filter_type)

    # Pagination
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')

    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    # Type counts
    type_counts = notifications.aggregate(
        info_count=Count('id', filter=Q(notification_type='info')),
        warning_count=Count('id', filter=Q(notification_type='warning')),
        success_count=Count('id', filter=Q(notification_type='success')),
        error_count=Count('id', filter=Q(notification_type='error')),
        reminder_count=Count('id', filter=Q(notification_type='reminder')),
    )

    context = {
        'notifications': notifications_page,
        'type_counts': type_counts,
        'filter_type': filter_type,
        'title': 'Sent Notifications'
    }
    return render(request, 'notification/sent_notifications.html', context)


@login_required(login_url='/')
def notification_detail(request, pk):
    """View to display notification detail and mark as read"""
    notification = get_object_or_404(
        Notification,
        pk=pk,
        recipient=request.user
    )

    # Mark as read if not already read
    if not notification.is_read:
        notification.mark_as_read()

    context = {
        'notification': notification,
        'title': notification.title
    }
    return render(request, 'notification/notification_detail.html', context)


@login_required(login_url='/')
@require_POST
def mark_as_read(request, pk):
    """AJAX view to mark notification as read"""
    try:
        notification = Notification.objects.get(
            pk=pk,
            recipient=request.user
        )
        notification.mark_as_read()

        return JsonResponse({
            'status': 'success',
            'message': 'Notification marked as read'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Notification not found'
        }, status=404)


@login_required(login_url='/')
@require_POST
def mark_multiple_as_read(request):
    """AJAX view to mark multiple notifications as read"""
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids[]')

        if notification_ids:
            notifications = Notification.objects.filter(
                id__in=notification_ids,
                recipient=request.user,
                is_read=False
            )
            count = notifications.update(is_read=True)

            return JsonResponse({
                'status': 'success',
                'message': f'{count} notifications marked as read'
            })

        return JsonResponse({
            'status': 'error',
            'message': 'No notifications selected'
        }, status=400)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)


@login_required(login_url='/')
@require_POST
def delete_notification(request, pk):
    """AJAX view to soft delete a notification"""
    try:
        notification = Notification.objects.get(
            pk=pk,
            recipient=request.user
        )
        notification.delete()

        return JsonResponse({
            'status': 'success',
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Notification not found'
        }, status=404)


@login_required(login_url='/')
def get_unread_count(request):
    """AJAX view to get unread notification count"""
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return JsonResponse({
        'unread_count': unread_count
    })


@login_required(login_url='/')
def get_recent_notifications(request):
    """AJAX view to get recent notifications for dropdown/header"""
    limit = int(request.GET.get('limit', 5))

    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('sender')[:limit]

    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message[:100] + ('...' if len(notification.message) > 100 else ''),
            'notification_type': notification.notification_type,
            'sender': notification.sender.username,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%b %d, %Y %H:%M'),
            'time_ago': _get_time_ago(notification.created_at)
        })

    return JsonResponse({
        'notifications': notifications_data
    })


@login_required(login_url='/')
@require_POST
@role_required('1', '3', '4')  # Admin, Department Head, HR
def quick_send_notification(request):
    """AJAX view to quickly send a notification from the dropdown"""
    try:
        recipient_id = request.POST.get('recipient_id')
        message = request.POST.get('message', '').strip()
        
        if not recipient_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Please select a recipient'
            }, status=400)
        
        if not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Please enter a message'
            }, status=400)
        
        recipient = CustomUser.objects.get(id=recipient_id, is_active=True)
        
        # Create notification
        notification = Notification.objects.create(
            sender=request.user,
            recipient=recipient,
            title=f"Message from {request.user.get_full_name() or request.user.username}",
            message=message,
            notification_type='info',
            is_active=True
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification sent successfully',
            'notification_id': notification.id
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Recipient not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error sending notification: {str(e)}'
        }, status=500)


@login_required(login_url='/')
@role_required('1', '3', '4')  # Admin, Department Head, HR
def get_users_for_notification(request):
    """AJAX view to get list of users for notification dropdown"""
    users = CustomUser.objects.filter(is_active=True).exclude(id=request.user.id).order_by('first_name', 'last_name')
    
    user_type_map = {
        '1': 'Admin',
        '2': 'Employee',
        '3': 'Department Head',
        '4': 'HR'
    }
    
    users_data = []
    for user in users:
        user_type_label = user_type_map.get(str(user.user_type), 'User')
        users_data.append({
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'email': user.email,
            'user_type': user_type_label
        })
    
    return JsonResponse({
        'users': users_data
    })


def _get_time_ago(datetime_obj):
    """Helper function to format time ago"""
    from django.utils import timezone
    import math

    now = timezone.now()
    diff = now - datetime_obj

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = math.floor(diff.seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = math.floor(diff.seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
