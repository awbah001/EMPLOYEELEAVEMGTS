# Staff Leave Management System - Enhancement Summary

## Overview
This document summarizes the comprehensive enhancements made to the Staff Leave Management System to support multiple user roles with proper RBAC (Role-Based Access Control).

## New User Roles Added

### 1. Super Admin (User Type: 1)
**Responsibilities:**
- Create, edit, or deactivate user accounts
- Assign roles (Staff, Department Head, HR, Super Admin)
- Manage system-wide settings
- Configure authentication (Google login, SSO)
- Full permission control and access oversight
- Manage departments

**New Routes:**
- `/SuperAdmin/Home` - Dashboard
- `/SuperAdmin/Users` - Manage users
- `/SuperAdmin/Roles/Assign` - Assign roles
- `/SuperAdmin/Departments` - Manage departments
- `/SuperAdmin/Settings` - System settings
- `/SuperAdmin/Auth/Config` - Authentication configuration

### 2. Department Head / Supervisor (User Type: 3)
**Responsibilities:**
- Review leave applications from staff in their department
- Approve or reject leave
- View departmental leave calendar
- Manage team schedules

**New Routes:**
- `/DepartmentHead/Home` - Dashboard
- `/DepartmentHead/Review/Leaves` - Review leave applications
- `/DepartmentHead/Calendar` - Departmental calendar
- `/DepartmentHead/Team/Schedules` - Team schedules

### 3. HR / Registry Department (User Type: 4)
**Responsibilities:**
- Add and update staff information
- Define leave types (annual, sick, study leave, maternity, etc.)
- Set leave entitlements
- Manually approve or override leave
- Generate reports
- Manage public holidays/academic breaks

**New Routes:**
- `/HR/Home` - Dashboard
- `/HR/Staff/Manage` - Manage staff
- `/HR/LeaveTypes/Manage` - Manage leave types
- `/HR/Entitlements/Set` - Set leave entitlements
- `/HR/Leave/Approve` - Approve/override leave
- `/HR/Reports` - Generate reports
- `/HR/Holidays/Manage` - Manage public holidays

### 4. Staff / Employees (User Type: 2) - Enhanced
**Existing Responsibilities (Verified):**
- ✅ Ability to log in
- ✅ Apply for leave
- ✅ View leave balance (NEW)
- ✅ Track leave application status (NEW)
- ✅ View full leave history

**New Routes:**
- `/Staff/Leave/Balance` - View leave balance
- `/Staff/Leave/Track/<leave_id>` - Track specific leave status

## Database Models Added

### 1. Department
- `name` - Department name
- `description` - Department description
- Links staff to departments

### 2. DepartmentHead
- Links a user to a department as head
- One department can have multiple heads

### 3. LeaveType
- `name` - Leave type name (Annual, Sick, Maternity, etc.)
- `description` - Description
- `max_days_per_year` - Maximum days allowed
- `requires_approval` - Whether approval is needed
- `is_active` - Active status

### 4. LeaveEntitlement
- Links staff to leave types with entitlements per year
- `days_entitled` - Days entitled for the year

### 5. LeaveBalance
- Tracks leave balance for each staff member
- `days_entitled` - Total days entitled
- `days_used` - Days used
- `days_remaining` - Automatically calculated

### 6. PublicHoliday
- Manages public holidays and academic breaks
- `name` - Holiday name
- `date` - Holiday date
- `is_active` - Active status

### 7. SystemSettings
- Stores system-wide configuration
- Key-value pairs for settings

## Enhanced Models

### CustomUser
- Updated user types: (1: Super Admin, 2: Staff, 3: Department Head, 4: HR)
- Profile picture made optional

### Staff
- Added `department` - ForeignKey to Department
- Added `employee_id` - Unique employee identifier
- Added `phone_number` - Contact number
- Added `date_of_joining` - Joining date

### Staff_Leave
- Changed `from_date` and `to_date` from CharField to DateField
- Added `leave_type` - ForeignKey to LeaveType
- Kept `leave_type_name` for backward compatibility
- Added `approved_by_department_head` - Tracks who approved
- Added `approved_by_hr` - Tracks HR approval
- Added `rejection_reason` - Reason for rejection
- Added status choices with proper labels

## New Files Created

### Views
1. `slms/decorators.py` - Role-based access control decorators
2. `slms/departmentheadviews.py` - Department Head views
3. `slms/hrviews.py` - HR views
4. `slms/superadminviews.py` - Super Admin views

### Updated Files
1. `slmsapp/models.py` - All new models and enhancements
2. `slms/staffviews.py` - Enhanced with leave balance and tracking
3. `slms/views.py` - Updated login redirects for new roles
4. `slms/urls.py` - Added all new routes
5. `slms/adminviews.py` - Updated to work with departments

## Permission System

### Decorators Created
- `@role_required(*allowed_roles)` - Generic role checker
- `@super_admin_required` - Super Admin only
- `@staff_required` - Staff only
- `@department_head_required` - Department Head only
- `@hr_required` - HR only
- `@admin_or_hr_required` - Super Admin or HR

## Migration Instructions

### Step 1: Create Migration
```bash
cd staffleave/slms
python manage.py makemigrations
```

### Step 2: Review Migration
Check the generated migration file in `slmsapp/migrations/` to ensure all changes are captured.

### Step 3: Handle Data Migration (if needed)
If you have existing data with CharField dates in Staff_Leave, you may need to create a data migration to convert them to DateField format.

### Step 4: Apply Migration
```bash
python manage.py migrate
```

### Step 5: Create Initial Data
You may want to create:
1. Default departments
2. Default leave types (Annual, Sick, Maternity, etc.)
3. Assign departments to existing staff
4. Create Department Head records for existing department heads

## Important Notes

1. **Backward Compatibility**: The system maintains backward compatibility with existing data:
   - `leave_type_name` field kept for old leave records
   - Old admin views still work but redirect to new views based on role

2. **Date Fields**: `from_date` and `to_date` in Staff_Leave are now DateField. If you have existing data with string dates, you'll need a data migration.

3. **User Types**: 
   - Old: 1=admin, 2=staff
   - New: 1=Super Admin, 2=Staff, 3=Department Head, 4=HR
   - Existing admin users (type 1) will be treated as Super Admin
   - Existing staff (type 2) remain as Staff

4. **Department Assignment**: Existing staff will have `department=None`. You should assign departments after migration.

5. **Leave Types**: You need to create LeaveType records before staff can apply for leave with the new system. Old leave applications will still work with `leave_type_name`.

## Testing Checklist

- [ ] Create Super Admin user and test all Super Admin functions
- [ ] Create Department Head and assign to department
- [ ] Create HR user and test HR functions
- [ ] Test staff applying for leave
- [ ] Test Department Head approving/rejecting leave
- [ ] Test HR managing leave types and entitlements
- [ ] Test leave balance calculation
- [ ] Test report generation
- [ ] Test public holiday management
- [ ] Test role assignment
- [ ] Test user activation/deactivation

## Next Steps

1. Run migrations
2. Create initial departments
3. Create initial leave types
4. Assign departments to staff
5. Create Department Head records
6. Set up leave entitlements for staff
7. Test all functionality
8. Create templates for new views (if not already created)

## Template Requirements

The following templates need to be created (or updated):
- `templates/superadmin/` - All Super Admin templates
- `templates/departmenthead/` - All Department Head templates
- `templates/hr/` - All HR templates
- `templates/staff/leave_balance.html` - Leave balance view
- `templates/staff/track_leave.html` - Track leave status

## Support

For issues or questions, refer to the code comments in the respective view files or model files.

