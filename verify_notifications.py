#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
project_path = os.path.join(os.path.dirname(__file__), 'staffleave', 'slms')
sys.path.insert(0, project_path)

os.chdir(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slms.settings')
django.setup()

from slmsapp.models import Notification, Employee_Leave

# Get the latest leave end notification
notifications = Notification.objects.filter(
    title__contains='Leave Ended'
).order_by('-created_at')

print("=" * 70)
print("LEAVE END NOTIFICATION VERIFICATION")
print("=" * 70)

if notifications.exists():
    notif = notifications.first()
    print(f"\n✓ Latest Leave End Notification:")
    print(f"  Title: {notif.title}")
    print(f"  Message: {notif.message}")
    print(f"  Recipient: {notif.recipient.username}")
    print(f"  Sender: {notif.sender.username}")
    print(f"  Type: {notif.notification_type}")
    print(f"  Created: {notif.created_at}")
else:
    print("\n✗ No leave ended notifications found")

# Check ended leaves status
ended_leaves = Employee_Leave.objects.filter(leave_end_notification_sent=True)
print(f"\n✓ Total leaves with notifications sent: {ended_leaves.count()}")

# Show recent leaves with notifications
print(f"\nRecent notified leaves:")
for leave in ended_leaves.order_by('-to_date')[:5]:
    print(f"  - {leave.employee_id.admin.username}: {leave.from_date} to {leave.to_date}")

print("\n" + "=" * 70)
