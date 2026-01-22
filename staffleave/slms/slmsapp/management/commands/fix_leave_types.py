"""
Management command to fix leave types before migration
Run this BEFORE running migrate if migration 0007 failed
"""
from django.core.management.base import BaseCommand
from django.db import connection
from slmsapp.models import LeaveType, Employee_Leave


class Command(BaseCommand):
    help = 'Fix leave types data before migration - copies leave_type to leave_type_name and creates LeaveType records'

    def handle(self, *args, **options):
        self.stdout.write('Fixing leave types data...')
        
        # Get all unique leave types from existing Employee_Leave records
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT leave_type FROM slmsapp_staff_leave WHERE leave_type IS NOT NULL AND leave_type != ''")
            rows = cursor.fetchall()
            leave_types_set = {row[0] for row in rows if row[0]}
        
        self.stdout.write(f'Found {len(leave_types_set)} unique leave types: {leave_types_set}')
        
        # Create LeaveType records
        created_count = 0
        for lt_name in leave_types_set:
            if lt_name and lt_name.strip():
                leave_type, created = LeaveType.objects.get_or_create(
                    name=lt_name.strip(),
                    defaults={
                        'max_days_per_year': 0,
                        'requires_approval': True,
                        'is_active': True,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created LeaveType: {lt_name}'))
        
        # Update leave_type_name for all records
        updated_count = 0
        for leave in Employee_Leave.objects.all():
            if leave.leave_type and isinstance(leave.leave_type, str):
                if not leave.leave_type_name or leave.leave_type_name != leave.leave_type:
                    leave.leave_type_name = leave.leave_type
                    leave.save(update_fields=['leave_type_name'])
                    updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\nCompleted:\n'
            f'  - Created {created_count} new LeaveType records\n'
            f'  - Updated {updated_count} Employee_Leave records with leave_type_name'
        ))
        
        self.stdout.write(self.style.WARNING(
            '\nNow you can run: python manage.py migrate'
        ))

