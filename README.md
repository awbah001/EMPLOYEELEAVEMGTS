# 🌿 HarmonyLeave - Staff Leave Management System (SLMS)

A comprehensive, professional-grade Django web application for managing employee leave requests and departmental schedules within an organization. HarmonyLeave provides a modern, intuitive interface with robust role-based access control, multi-level approval workflows, and real-time notifications.

**Project Name:** HarmonyLeave E/SLMS  
**Technology Stack:** Django 4.2 + SQLite + Bootstrap + Material Design Icons

---

## 🎯 Overview

HarmonyLeave is a complete Leave Management System designed to streamline leave request processes across organizations of any size. The system supports complex approval hierarchies, comprehensive reporting, and seamless notifications.

### Core Capabilities
- **Role-Based Access Control:** 4 distinct user roles with granular permissions
- **Multi-Level Approval Workflow:** Department Head → HR approval chain
- **Leave Balance Management:** Real-time tracking of entitlements and usage
- **Department-Based Organization:** Organize employees by departments with designated heads
- **Calendar Integration:** Interactive calendars with leave visualization
- **Notification System:** Email and in-app notifications for all leave events
- **Document Management:** Support for uploading supporting documents with requests
- **Analytics & Reports:** Comprehensive dashboards for leave statistics
- **Public Holidays & Events:** Centralized management of organizational calendar
- **User Profiles:** Complete employee profile management with photo uploads
- **Modern, Responsive UI:** Professional design with gradient cards, smooth animations, and mobile responsiveness

---

## 🚀 Key Features

### Leave Management
- **Submit Leave Requests:** Employees can apply for leave with multiple leave types
- **Approval Workflow:** Two-stage approval process (Department Head → HR)
- **Leave Balance Tracking:** Automatic calculation of remaining leave days
- **Supporting Documents:** Upload relevant documents with leave requests
- **Leave History:** Complete audit trail of all leave requests and actions
- **Multiple Leave Types:** Support for Annual, Sick, Casual, Maternity, Paternity, etc.
- **Leave Entitlements:** Set annual leave entitlements per employee per leave type

### Department Management
- **Department Organization:** Organize staff into departments
- **Department Heads:** Assign department heads as approvers
- **Departmental Views:** Filter and view department-specific data
- **Team Schedules:** Manage team availability and schedules

### Calendar Features
- **Interactive Calendars:** Visual representation of all leave and events
- **Holiday Management:** Define public holidays and recurring holidays
- **Calendar Events:** Create and manage organizational events (meetings, training, etc.)
- **User-Specific Views:** Each role sees only relevant calendar data

### Notifications
- **Real-Time Notifications:** Instant in-app notifications for all events
- **Email Notifications:** Email alerts for important leave events
- **Notification Types:** Info, Warning, Success, Error, Reminder
- **Read Status Tracking:** Track which notifications users have viewed

### Analytics & Reporting
- **Dashboard Analytics:** Visual representation of leave statistics
- **Leave Statistics:** Track approved, rejected, and pending leaves
- **Employee Reports:** Generate reports by department or individual
- **Leave Patterns:** Analyze organizational leave trends

### User Profiles
- **Personal Information:** Manage employee details (phone, address, etc.)
- **Profile Pictures:** Upload and manage profile photos
- **Employment Information:** Track employment type and joining date
- **Password Management:** Secure password change functionality

---

## 📁 Project Structure

```
Staff-Leave-MS-Django-Python/
│
├── staffleave/                          # Main project directory
│   ├── slms/                            # Django project folder
│   │   ├── slms/                        # Core Django app
│   │   │   ├── __init__.py
│   │   │   ├── settings.py              # Django configuration
│   │   │   ├── urls.py                  # URL routing
│   │   │   ├── wsgi.py                  # WSGI configuration
│   │   │   ├── asgi.py                  # ASGI configuration
│   │   │   ├── views.py                 # Common views (login, profile, etc.)
│   │   │   ├── adminviews.py            # Admin/Super Admin portal views
│   │   │   ├── hrviews.py               # HR portal views
│   │   │   ├── departmentheadviews.py   # Department Head portal views
│   │   │   ├── staffviews.py            # Employee portal views
│   │   │   ├── notificationviews.py     # Notification views
│   │   │   ├── auth_utils.py            # Authentication utilities
│   │   │   ├── leave_utils.py           # Leave calculation utilities
│   │   │   ├── notification_utils.py    # Notification utilities
│   │   │   ├── context_processors.py    # Context processors
│   │   │   ├── decorators.py            # Permission decorators
│   │   │   └── password_reset_views.py  # Password reset views
│   │   │
│   │   ├── slmsapp/                     # Main app with models and logic
│   │   │   ├── __init__.py
│   │   │   ├── models.py                # Data models (Employee, Leave, etc.)
│   │   │   ├── views.py                 # App views
│   │   │   ├── forms.py                 # Form definitions
│   │   │   ├── admin.py                 # Django admin configuration
│   │   │   ├── apps.py
│   │   │   ├── tests.py
│   │   │   ├── EmailBackEnd.py          # Custom email authentication backend
│   │   │   ├── migrations/              # Database migrations
│   │   │   │   └── ... (20+ migrations)
│   │   │   └── management/
│   │   │       └── commands/
│   │   │
│   │   ├── templates/                   # HTML templates
│   │   │   ├── base.html                # Base template with sidebar/navbar
│   │   │   ├── login.html               # Login page
│   │   │   ├── firstpage.html           # Landing page
│   │   │   ├── profile.html             # User profile page
│   │   │   ├── change-password.html     # Password change page
│   │   │   ├── admin/                   # Admin portal templates (20+ files)
│   │   │   ├── hr/                      # HR portal templates (15+ files)
│   │   │   ├── departmenthead/          # Department Head templates
│   │   │   ├── staff/                   # Employee portal templates
│   │   │   ├── notification/            # Notification templates
│   │   │   ├── includes/                # Reusable template components
│   │   │   └── registration/            # Registration templates
│   │   │
│   │   ├── static/                      # Static files (CSS, JS, images)
│   │   │   └── assets/
│   │   │       ├── css/                 # Stylesheets
│   │   │       ├── js/                  # JavaScript files
│   │   │       ├── images/              # Icons and images
│   │   │       └── plugins/             # Third-party libraries
│   │   │
│   │   ├── media/                       # User-uploaded files
│   │   │   ├── profile_pic/             # Profile pictures
│   │   │   └── leave_documents/         # Leave supporting documents
│   │   │
│   │   ├── db.sqlite3                   # SQLite database (development)
│   │   ├── manage.py                    # Django management script
│   │   └── __init__.py
│   │
│   └── ... (configuration files)
│
├── .git/                                # Git repository
├── .gitignore                           # Git ignore rules
├── Installation_guide.docx              # Installation documentation
├── README.md                            # This file
└── verify_notifications.py              # Notification verification script
```

### Key Directories Explained
- **slms/slms/:** Core Django configuration and role-specific views
- **slmsapp/:** Data models and business logic
- **templates/:** HTML templates organized by user role
- **static/:** CSS, JavaScript, and image assets
- **media/:** User uploads (profile pictures, documents)

---

## ⚙️ Installation & Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- SQLite (included with Python)

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd Staff-Leave-MS-Django-Python/staffleave/slms
```

### 2. Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install django==4.2
pip install pillow
pip install python-decouple
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account. You'll use these credentials to log in.

### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

### 7. Access the System
- **Login Page:** http://127.0.0.1:8000/Login
- **First Page:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## 🔑 User Roles & Permissions

The system includes 4 distinct user roles, each with specific permissions and features:

### 1. 🏆 Super Admin / Admin (`user_type = '1'`)
**Portal:** `/Admin/Home`

**Permissions:**
- Full system access and complete control
- User management (create, edit, deactivate, delete users)
- Role assignment and role management
- Department management and configuration
- View all leaves across the entire organization (all statuses)
- Leave approval/rejection override authority
- Public holidays and calendar events management
- System settings configuration
- Leave type management
- Analytics and reporting dashboard
- View complete organizational leave calendar

**Key Features:**
- User Management Dashboard
- Department Configuration
- System-wide Analytics
- Public Holiday Management
- Calendar Event Management

**Access:** Dashboard → Admin Home (requires admin user_type)

---

### 2. 💼 HR (Human Resources) (`user_type = '4'`)
**Portal:** `/HR/Home`

**Permissions:**
- Manage employee records and information
- Create and manage leave types
- Set and configure leave entitlements
- Approve/reject leave requests (final approval stage)
- View all approved leaves across organization
- Generate HR reports and statistics
- Public holiday management
- Leave balance management
- Calendar access (approved leaves only)

**Key Features:**
- Employee Management
- Leave Type Configuration
- Leave Entitlement Setting
- Leave Application Review
- HR Analytics Dashboard
- Holiday Management
- Bulk Entitlement Setup

**Access:** Dashboard → HR Home (requires HR user_type)

**Leave Approval Flow:** Department Head approval → HR final approval

---

### 3. 👔 Department Head (`user_type = '3'`)
**Portal:** `/DepartmentHead/Home`

**Permissions:**
- Review and manage leave requests from department staff only
- First-level approval of leave requests
- View departmental leave calendar and analytics
- Manage team schedules
- View all leave statuses for department members (pending, approved, rejected)
- Department-specific reporting
- Team availability management

**Key Features:**
- Departmental Dashboard
- Leave Application Review & Approval
- Department-specific Calendar
- Team Schedule Management
- Department Analytics
- Employee Directory (department members)

**Access:** Dashboard → Department Head Home (requires DH user_type)

**Capabilities:**
- Approve pending leaves from staff
- Reject leaves with reasons
- View team availability
- Monitor department leave patterns

---

### 4. 👤 Employee / Staff (`user_type = '2'`)
**Portal:** `/Employee/Home`

**Permissions:**
- Submit personal leave applications
- Upload supporting documents with requests
- View personal leave history and status
- Check personal leave balance by type
- Update personal profile and information
- View personal calendar (own leaves only)
- Change password
- View personal notifications

**Key Features:**
- Leave Application Form
- Leave History & Tracking
- Leave Balance Viewer
- Personal Calendar
- Document Upload
- Profile Management
- Notification Center

**Access:** Dashboard → Employee Home (requires staff user_type)

**Leave Application Workflow:**
1. Submit leave request with details and optional documents
2. Status = Pending (awaiting Department Head approval)
3. Department Head reviews → Approves/Rejects
4. If approved → Status = Pending (awaiting HR approval)
5. HR reviews → Final Approval/Rejection
6. Status = Approved or Rejected

---

## 📋 Setting Up Users & Roles

### Via Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Navigate to "Users" or use "Manage Users" in Django admin
4. Create new user and set `user_type`:
   - **1** = Admin/Super Admin
   - **2** = Employee/Staff
   - **3** = Department Head
   - **4** = HR

### Via Web Interface
1. Login as Admin
2. Go to Admin Panel → Manage Users
3. Create new user
4. Assign role from dropdown
5. If Department Head: assign to a department
6. Click Save

**Important:** Always verify `user_type` is correctly set to ensure proper access to user portals.

---

## 📅 Calendar Features

The system includes comprehensive calendar functionality with user-specific views:

### Staff Calendar
- View only your own leave requests
- See leave status (pending, approved, rejected) on calendar dates
- View public holidays and calendar events
- Visual indicators for different leave statuses
- Access via: Sidebar → Employee → Calendar

### Admin Calendar
- View all leaves across entire organization
- See all leave statuses (pending, approved, rejected)
- Filter by department or employee
- Comprehensive organizational overview
- Access via: Sidebar → Admin → Calendar

### HR Calendar
- View all approved leaves across organization
- Monitor organization-wide leave patterns
- Track leave distribution
- Plan workforce availability
- Access via: Sidebar → HR → Calendar

### Department Head Calendar
- View only leaves from your department staff
- See all leave statuses for department members
- Plan team schedules
- Identify coverage gaps
- Access via: Sidebar → Department Head → Calendar

**Calendar Legend:**
- 🟢 Green = Approved leave
- 🟡 Yellow = Pending leave
- 🔴 Red = Rejected leave
- 🟠 Orange = Public holiday
- 🔵 Blue = Calendar events

**Note:** Each calendar is user-specific - users only see leaves relevant to their role and permissions.

---

## 🛠 Troubleshooting & Common Issues

### Installation Issues

**Issue:** `ModuleNotFoundError: No module named 'django'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
# Or manually:
pip install django==4.2 pillow python-decouple
```

**Issue:** `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty`
```bash
# Solution: Check settings.py - SECRET_KEY should already be set
# If not, generate a new one in Django shell
```

**Issue:** `relation "slmsapp_customuser" does not exist`
```bash
# Solution: Run migrations
python manage.py migrate
```

### Runtime Issues

**Issue:** User cannot login or sees "Invalid credentials"
- Verify user account is active (is_active = True)
- Check user_type is correctly set (1=Admin, 2=Staff, 3=DH, 4=HR)
- Ensure CustomUser is being used (not default Django User model)
- Try resetting password via password reset link

**Issue:** Static files (CSS, Images) not loading
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput
# For development, ensure DEBUG = True in settings.py
```

**Issue:** Calendar appears empty
- Verify user_type is correctly set
- Check that leaves exist for the user's department/role
- Clear browser cache (Ctrl+Shift+Delete)
- Check browser console for JavaScript errors

**Issue:** Profile picture not uploading
- Verify MEDIA_URL and MEDIA_ROOT in settings.py
- Ensure media/ directory exists and is writable
- Check file size limits
- Try with different image format (JPG, PNG)

**Issue:** Notifications not appearing
- Check Notification table in admin panel
- Verify sender and recipient users exist
- Check is_active flag on notifications
- Look for database transaction issues

**Issue:** Leave balance showing incorrect numbers
- Verify leave entitlements are set correctly
- Check for duplicate leave applications
- Review leave balance calculation in models.py
- Ensure approved leaves are actually marked as approved

### Database Issues

**Reset Database (Development Only):**
```bash
# WARNING: This deletes all data!
# 1. Delete db.sqlite3
# 2. Delete all migration files except __init__.py
# 3. Run migrations:
python manage.py migrate
python manage.py createsuperuser
```

**Backup Database:**
```bash
# Copy db.sqlite3 to a safe location
cp db.sqlite3 db.sqlite3.backup
```

### Performance Issues

**Issue:** Slow page loading
- Enable query logging to identify slow queries
- Consider adding database indexes
- Clear cache: `python manage.py clear_cache`
- Check for N+1 query problems in views

**Issue:** High CPU usage
- Check for infinite loops in JavaScript
- Review background tasks if any
- Monitor database query count
- Profile views with Django Debug Toolbar

---

## 🔐 Security Best Practices

### For Production Deployment

1. **Change SECRET_KEY:**
   - Generate a secure random key
   - Store in environment variable
   - Never commit to version control

2. **Set DEBUG = False:**
   - In settings.py
   - Shows generic error pages instead of debug info
   - Prevents information leakage

3. **Set ALLOWED_HOSTS:**
   - List all allowed domains
   - Prevents host header attacks
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Use HTTPS:**
   - Configure SSL/TLS certificate
   - Set `SECURE_SSL_REDIRECT = True`

5. **Database Security:**
   - Don't use default SQLite for production
   - Use PostgreSQL or MySQL
   - Set strong database password
   - Regular database backups

6. **File Upload Security:**
   - Validate file types
   - Limit file sizes
   - Store outside web root
   - Scan for malware

7. **Password Policy:**
   - Enforce strong passwords
   - Set password expiration (if needed)
   - Enable 2FA (if needed)

---

## 📚 System Architecture

### Technology Stack
- **Backend:** Django 4.2 (Python web framework)
- **Database:** SQLite (development) / PostgreSQL (production recommended)
- **Frontend:** HTML5, CSS3, JavaScript
- **UI Components:** Material Design Icons, Bootstrap Classes
- **Authentication:** Email-based custom backend
- **File Storage:** Django FileField with media management

### Key Models
```
CustomUser (extends Django User)
    ├── Employee
    │   ├── Department
    │   ├── Employee_Leave
    │   │   ├── LeaveType
    │   │   └── [supporting_document]
    │   └── LeaveBalance
    │       └── LeaveType
    ├── DepartmentHead
    │   └── Department
    ├── Notification
    │   ├── sender (CustomUser)
    │   └── recipient (CustomUser)
    └── ...
```

### Data Flow

1. **User Login** → CustomUser authentication → Role check
2. **Leave Request** → Create Employee_Leave → Notify Department Head
3. **Approval** → Update Employee_Leave status → Notify HR
4. **Final Approval** → Update Employee_Leave → Update LeaveBalance
5. **Notification** → Create Notification record → Send to recipient

---

## 🚀 Deployment Guide

### Development Deployment
```bash
# Already covered in Quick Start section
python manage.py runserver
# Access at http://127.0.0.1:8000/
```

### Production Deployment Options

**Option 1: Using Gunicorn + Nginx**
```bash
pip install gunicorn
gunicorn slms.wsgi:application --bind 0.0.0.0:8000
# Configure Nginx as reverse proxy
```

**Option 2: Using Docker**
- Create Dockerfile (not provided, but simple to set up)
- Use docker-compose for orchestration
- Mount volumes for database and media files

**Option 3: Cloud Platforms**
- Heroku: `git push heroku main`
- AWS: Use Elastic Beanstalk or EC2
- Google Cloud: App Engine or Compute Engine
- Azure: App Service

### Database Migration to Production
```bash
# Export data from SQLite
python manage.py dumpdata > db.json

# Switch to PostgreSQL in settings
# Run migrations
python manage.py migrate

# Import data
python manage.py loaddata db.json
```

---

## 📖 Additional Resources

### Files in Project
- **requirements.txt** - Python dependencies
- **Installation_guide.docx** - Detailed installation steps
- **manage.py** - Django management utility
- **db.sqlite3** - Development database

### External Resources
- Django Documentation: https://docs.djangoproject.com/
- Material Design Icons: https://fonts.google.com/icons
- Bootstrap CSS: https://getbootstrap.com/

### Support & Contributions
- Review code comments for implementation details
- Check migrations for database schema
- Examine views for business logic
- Review templates for UI structure

---

## ✅ Feature Checklist

- [x] Multi-role user system
- [x] Leave request workflow
- [x] Approval process (2-level)
- [x] Leave balance tracking
- [x] Calendar views
- [x] Public holidays
- [x] Notifications
- [x] Document upload
- [x] Analytics dashboard
- [x] Profile management
- [x] Department management
- [x] Responsive design
- [x] Email authentication
- [x] Password reset

---

## 📝 License & Usage

This project is provided as-is for organizational use. Feel free to:
- ✅ Use in your organization
- ✅ Modify for your needs
- ✅ Deploy internally
- ✅ Extend functionality

Please note:
- ❌ No warranty provided
- ❌ Use at your own discretion
- ⚠️ Ensure proper backups
- ⚠️ Test thoroughly before production

---

**Last Updated:** January 2026  
**Version:** 1.0 (Production Ready)

For questions or support, review the troubleshooting section or examine the source code comments.
