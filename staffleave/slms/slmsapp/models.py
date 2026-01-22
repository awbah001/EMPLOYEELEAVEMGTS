from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class CustomUser(AbstractUser):
    USER ={
        (1,'Admin'),
        (2,'Employee'),
        (3,'Department Head'),
        (4,'HR')
    }
    user_type = models.CharField(choices=USER,max_length=50,default=2)
    # is_active is already in AbstractUser, no need to redefine

    profile_pic = models.ImageField(upload_to='media/profile_pic', blank=True, null=True)

    def __str__(self):
        return self.username


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary'),
        ('Intern', 'Intern'),
    ]
    
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    employee_type = models.CharField(max_length=50, choices=EMPLOYEE_TYPE_CHOICES, default='Full-time', blank=True, null=True, db_column='staff_type')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_members')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.username
    
    @staticmethod
    def generate_employee_id():
        """Generate a unique employee ID in the format EMP001, EMP002, etc."""
        # Get the highest existing employee ID number
        last_employee = Employee.objects.filter(employee_id__isnull=False).exclude(employee_id='').order_by('employee_id').last()
        
        if last_employee and last_employee.employee_id:
            # Try to extract number from existing IDs (handle formats like EMP001, EMP1, etc.)
            import re
            match = re.search(r'(\d+)', last_employee.employee_id)
            if match:
                last_num = int(match.group(1))
                new_num = last_num + 1
            else:
                # If no number found, start from 1
                new_num = 1
        else:
            # No existing IDs, start from 1
            new_num = 1
        
        # Format as EMP001, EMP002, etc. (3-digit padding)
        employee_id = f"EMP{new_num:03d}"
        
        # Ensure uniqueness (in case of gaps or manual entries)
        while Employee.objects.filter(employee_id=employee_id).exists():
            new_num += 1
            employee_id = f"EMP{new_num:03d}"
        
        return employee_id
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate employee_id if not provided"""
        if not self.employee_id:
            self.employee_id = self.generate_employee_id()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'slmsapp_staff'  # Keep using existing table name


class DepartmentHead(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_heads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin.username} - {self.department.name}"

    class Meta:
        verbose_name = "Department Head"
        verbose_name_plural = "Department Heads"


class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    max_days_per_year = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Leave Type"
        verbose_name_plural = "Leave Types"


class LeaveEntitlement(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_entitlements', db_column='staff_id')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    days_entitled = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
        verbose_name = "Leave Entitlement"
        verbose_name_plural = "Leave Entitlements"

    def __str__(self):
        return f"{self.employee.admin.username} - {self.leave_type.name} ({self.year})"


class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances', db_column='staff_id')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    days_entitled = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_used = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_remaining = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
        verbose_name = "Leave Balance"
        verbose_name_plural = "Leave Balances"

    def __str__(self):
        return f"{self.employee.admin.username} - {self.leave_type.name} ({self.year})"

    def save(self, *args, **kwargs):
        self.days_remaining = self.days_entitled - self.days_used
        super().save(*args, **kwargs)


class Employee_Leave(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    ]

    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications', db_column='staff_id_id')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)
    leave_type_name = models.CharField(max_length=100, blank=True, null=True)  # Keep for backward compatibility
    from_date = models.DateField()
    to_date = models.DateField()
    message = models.TextField()
    supporting_document = models.FileField(upload_to='leave_documents/', null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    approved_by_department_head = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves_dh')
    approved_by_hr = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves_hr')
    rejection_reason = models.TextField(blank=True, null=True)
    leave_end_notification_sent = models.BooleanField(default=False, null=True)  # Track if employee was notified when leave ended
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id.admin.first_name} {self.employee_id.admin.last_name} - {self.leave_type_name}"
    
    def get_document_filename(self):
        """Get the filename from the document path"""
        if self.supporting_document:
            return self.supporting_document.name.split('/')[-1]
        return None

    class Meta:
        db_table = 'slmsapp_staff_leave'  # Keep using existing table name
        verbose_name = "Employee Leave"
        verbose_name_plural = "Employee Leaves"
        ordering = ['-created_at']


class PublicHoliday(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'date']
        verbose_name = "Public Holiday"
        verbose_name_plural = "Public Holidays"
        ordering = ['date']

    def __str__(self):
        return f"{self.name} - {self.date}"


class CalendarEvent(models.Model):
    """General calendar events that can be added by admins"""
    EVENT_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('training', 'Training'),
        ('workshop', 'Workshop'),
        ('announcement', 'Announcement'),
        ('deadline', 'Deadline'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField()
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='other')
    location = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_all_day = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
        ordering = ['event_date', 'start_time']

    def __str__(self):
        return f"{self.title} - {self.event_date}"


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('reminder', 'Reminder'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_notifications')
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} -> {self.recipient.username}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])

    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.save(update_fields=['is_read', 'updated_at'])


class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.key

