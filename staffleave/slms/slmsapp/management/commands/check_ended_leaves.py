"""
Management command to check for ended leaves and send notifications
Run this daily via cron or scheduled task:
python manage.py check_ended_leaves
"""
from django.core.management.base import BaseCommand
from slms.notification_utils import check_and_notify_ended_leaves


class Command(BaseCommand):
    help = 'Check for leaves that ended and send notifications to staff'

    def handle(self, *args, **options):
        self.stdout.write('Checking for ended leaves...')
        
        notifications_sent = check_and_notify_ended_leaves()
        
        if notifications_sent > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {notifications_sent} notification(s) for ended leaves.'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('No ended leaves found to notify.'))

