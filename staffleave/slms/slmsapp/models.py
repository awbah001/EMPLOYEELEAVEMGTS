from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class CustomUser(AbstractUser):
    USER ={
        (1,'Admin'),
        (2,'Staff'),
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


class Staff(models.Model):
    STAFF_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Temporary', 'Temporary'),
        ('Intern', 'Intern'),
    ]
    
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    gender = models.CharField(max_length=100)
    staff_type = models.CharField(max_length=50, choices=STAFF_TYPE_CHOICES, default='Full-time', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.admin.username


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
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leave_entitlements')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    days_entitled = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['staff', 'leave_type', 'year']
        verbose_name = "Leave Entitlement"
        verbose_name_plural = "Leave Entitlements"

    def __str__(self):
        return f"{self.staff.admin.username} - {self.leave_type.name} ({self.year})"


class LeaveBalance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField()
    days_entitled = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_used = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    days_remaining = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['staff', 'leave_type', 'year']
        verbose_name = "Leave Balance"
        verbose_name_plural = "Leave Balances"

    def __str__(self):
        return f"{self.staff.admin.username} - {self.leave_type.name} ({self.year})"

    def save(self, *args, **kwargs):
        self.days_remaining = self.days_entitled - self.days_used
        super().save(*args, **kwargs)


class Staff_Leave(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    ]

    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leave_applications')
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.staff_id.admin.first_name} {self.staff_id.admin.last_name} - {self.leave_type_name}"
    
    def get_document_filename(self):
        """Get the filename from the document path"""
        if self.supporting_document:
            return self.supporting_document.name.split('/')[-1]
        return None

    class Meta:
        verbose_name = "Staff Leave"
        verbose_name_plural = "Staff Leaves"
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
