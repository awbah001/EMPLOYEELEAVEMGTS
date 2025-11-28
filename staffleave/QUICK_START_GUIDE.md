# Quick Start Guide - Enhanced Staff Leave Management System

## Immediate Next Steps

### 1. Apply Migrations
```bash
cd staffleave/slms
python manage.py migrate
```

**⚠️ Important**: If you have existing leave records with date strings, you may need to handle data migration separately.

### 2. Create Initial Data

#### Create Departments
You can do this via Django admin or create a management command:
```python
from slmsapp.models import Department

Department.objects.create(name="IT Department", description="Information Technology")
Department.objects.create(name="HR Department", description="Human Resources")
Department.objects.create(name="Finance Department", description="Finance and Accounting")
# Add more departments as needed
```

#### Create Leave Types
```python
from slmsapp.models import LeaveType

LeaveType.objects.create(name="Annual Leave", max_days_per_year=21, requires_approval=True)
LeaveType.objects.create(name="Sick Leave", max_days_per_year=10, requires_approval=True)
LeaveType.objects.create(name="Maternity Leave", max_days_per_year=90, requires_approval=True)
LeaveType.objects.create(name="Study Leave", max_days_per_year=5, requires_approval=True)
LeaveType.objects.create(name="Emergency Leave", max_days_per_year=3, requires_approval=True)
```

### 3. Assign Roles

#### Convert Existing Admin to Super Admin
Existing users with `user_type='1'` are already Super Admins.

#### Create Department Head
```python
from slmsapp.models import CustomUser, Department, DepartmentHead

# Get user and department
user = CustomUser.objects.get(username='hod_username')
department = Department.objects.get(name='IT Department')

# Update user type
user.user_type = '3'  # Department Head
user.save()

# Create DepartmentHead record
DepartmentHead.objects.create(admin=user, department=department)
```

#### Create HR User
```python
from slmsapp.models import CustomUser

user = CustomUser.objects.get(username='hr_username')
user.user_type = '4'  # HR
user.save()
```

### 4. Assign Departments to Staff
```python
from slmsapp.models import Staff, Department

staff = Staff.objects.get(admin__username='staff_username')
department = Department.objects.get(name='IT Department')
staff.department = department
staff.save()
```

### 5. Set Leave Entitlements
```python
from slmsapp.models import Staff, LeaveType, LeaveEntitlement, LeaveBalance
from datetime import date

staff = Staff.objects.get(admin__username='staff_username')
leave_type = LeaveType.objects.get(name='Annual Leave')
current_year = date.today().year

# Create entitlement
entitlement = LeaveEntitlement.objects.create(
    staff=staff,
    leave_type=leave_type,
    days_entitled=21,
    year=current_year
)

# Create balance
LeaveBalance.objects.create(
    staff=staff,
    leave_type=leave_type,
    year=current_year,
    days_entitled=21,
    days_used=0
)
```

## User Role Access

### Super Admin (Type 1)
- Dashboard: `/SuperAdmin/Home`
- Manage Users: `/SuperAdmin/Users`
- Assign Roles: `/SuperAdmin/Roles/Assign`
- Manage Departments: `/SuperAdmin/Departments`
- System Settings: `/SuperAdmin/Settings`
- Auth Config: `/SuperAdmin/Auth/Config`

### Department Head (Type 3)
- Dashboard: `/DepartmentHead/Home`
- Review Leaves: `/DepartmentHead/Review/Leaves`
- Calendar: `/DepartmentHead/Calendar`
- Team Schedules: `/DepartmentHead/Team/Schedules`

### HR (Type 4)
- Dashboard: `/HR/Home`
- Manage Staff: `/HR/Staff/Manage`
- Manage Leave Types: `/HR/LeaveTypes/Manage`
- Set Entitlements: `/HR/Entitlements/Set`
- Approve Leave: `/HR/Leave/Approve`
- Reports: `/HR/Reports`
- Manage Holidays: `/HR/Holidays/Manage`

### Staff (Type 2)
- Dashboard: `/Staff/Home`
- Apply Leave: `/Staff/Apply_Leave`
- View History: `/Staff/Leaveview`
- View Balance: `/Staff/Leave/Balance`
- Track Leave: `/Staff/Leave/Track/<leave_id>`

## Common Workflows

### Staff Applying for Leave
1. Staff logs in → `/Staff/Home`
2. Click "Apply for Leave" → `/Staff/Apply_Leave`
3. Select leave type, dates, add message
4. Submit → Status: Pending

### Department Head Approving Leave
1. Department Head logs in → `/DepartmentHead/Home`
2. Click "Review Leaves" → `/DepartmentHead/Review/Leaves`
3. View pending leaves from department staff
4. Approve or Reject with reason
5. Status changes to Approved/Rejected

### HR Managing System
1. HR logs in → `/HR/Home`
2. Create/Update leave types → `/HR/LeaveTypes/Manage`
3. Set entitlements for staff → `/HR/Entitlements/Set`
4. Approve/Override leaves → `/HR/Leave/Approve`
5. Generate reports → `/HR/Reports`
6. Manage holidays → `/HR/Holidays/Manage`

## Troubleshooting

### Issue: "Staff profile not found"
**Solution**: Ensure the user has a corresponding Staff record. Only users with `user_type='2'` should have Staff records.

### Issue: "Department Head profile not found"
**Solution**: Create a DepartmentHead record linking the user to a department.

### Issue: Date field errors
**Solution**: If you have old data with string dates, create a data migration to convert them.

### Issue: Leave balance not showing
**Solution**: Create LeaveBalance records for staff. This can be done via HR panel or management command.

## Testing the System

1. **Test Staff Functions:**
   - Login as staff
   - Apply for leave
   - View leave balance
   - Track leave status

2. **Test Department Head Functions:**
   - Login as department head
   - Review pending leaves
   - Approve/reject leaves
   - View calendar

3. **Test HR Functions:**
   - Login as HR
   - Create leave types
   - Set entitlements
   - Approve leaves
   - Generate reports

4. **Test Super Admin Functions:**
   - Login as super admin
   - Create users
   - Assign roles
   - Manage departments
   - Configure settings

## Notes

- All new views use role-based decorators for security
- Old admin views still work for backward compatibility
- Leave balance is calculated automatically when days_used changes
- Department Heads can only see/approve leaves from their department
- HR can override any leave decision
- Super Admin has full system access

