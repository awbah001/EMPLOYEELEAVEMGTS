# Staff Leave Management System (SLMS)

A professional Django-based web application designed for managing staff leave requests within an organization. This system allows both admins and staff to interact via role-based interfaces and includes a modern, responsive design for an enhanced user experience.

---

## 🚀 Features

### Core Features
- **Multi-Role Access Control:** Separate portals for Admin, HR, Department Head, and Staff with role-based permissions
- **Leave Application Workflow:** Complete leave management system with approval workflows
- **User-Specific Calendar Views:** Each user type sees relevant calendar data:
  - **Staff:** Only their own leave requests (pending, approved, rejected)
  - **Admin:** All leaves across the entire organization (all statuses)
  - **HR:** All approved leaves across the organization
  - **Department Head:** Only leaves from their department staff (all statuses)
- **Leave Balance Management:** Track leave entitlements and usage by leave type
- **Public Holidays & Events:** Manage and display public holidays and calendar events
- **User Profiles:** Profile management with photo upload and personal details
- **Modern Responsive UI:** Clean, modern design with sidebar navigation, gradient cards, and mobile-responsive layout
- **Email Authentication:** Custom email-based authentication backend
- **Leave Document Upload:** Support for uploading supporting documents with leave requests
- **Department Management:** Organize staff by departments with department head assignments
- **Leave Type Management:** Configure and manage different types of leave (Annual, Sick, etc.)

---

## 📁 Project Structure

```
Staff-Leave-MS-Django-Python/
│
├── staffleave/
│   ├── slms/             # Django main project (settings, urls, wsgi, asgi)
│   │   ├── slms/         # Core application views
│   │   │   ├── adminviews.py       # Admin portal views
│   │   │   ├── hrviews.py          # HR portal views
│   │   │   ├── departmentheadviews.py  # Department Head views
│   │   │   ├── staffviews.py       # Staff portal views
│   │   │   └── ...
│   │   └── ...
│   ├── slmsapp/          # Main application logic (models, views, admin, migrations)
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # HTML templates
│   │   ├── admin/        # Admin portal templates
│   │   ├── hr/           # HR portal templates
│   │   ├── departmenthead/  # Department Head templates
│   │   ├── staff/        # Staff portal templates
│   │   └── base.html     # Base template with sidebar
│   ├── media/            # User-uploaded files (profile pics, leave documents)
│   └── db.sqlite3        # Default SQLite database
├── venv/                 # Optional: Python virtual environment
└── README.md
```

---

## ⚙️ Quick Start

### 1. Clone and enter directory
```bash
cd Staff-Leave-MS-Django-Python/staffleave/slms
```

### 2. Set up a virtual environment (recommended)
```bash
python -m venv venv
venv\Scripts\activate                      # Windows
# or
source venv/bin/activate                    # macOS/Linux
```

### 3. Install dependencies
```bash
pip install django pillow
```

If you want to enable Google sign-in (OAuth), install django-allauth too:

```bash
pip install django-allauth
```

### 4. Apply migrations & create a superuser (admin)
```bash
python manage.py migrate
python manage.py createsuperuser
```

Note: After adding the new Social authentication pieces you may also need to create/update the allauth SocialApp entry (or configure via the Admin -> Social applications UI). The admin UI includes an "Authentication configuration" page where you can paste your Google client id & secret — this code will attempt to create/update the SocialApp for the current Site automatically.

### 5. Run the development server
```bash
python manage.py runserver
```
Go to http://127.0.0.1:8000/ in your browser.

---

## 🔑 User Roles & Permissions

### 1. Admin (`user_type = '1'`)
- Full system access and management
- View all leaves across the organization (all statuses: pending, approved, rejected)
- Manage users, departments, and system settings
- Manage public holidays and calendar events
- View organization-wide calendar

### 2. HR (`user_type = '4'`)
- Manage staff and leave types
- Set leave entitlements
- Approve/reject leave requests (after department head approval)
- View all approved leaves across the organization
- Generate reports and manage public holidays

### 3. Department Head (`user_type = '3'`)
- Review and approve/reject leave requests from their department staff
- View departmental calendar (only their department's leaves)
- Manage team schedules
- See all leave statuses for their department

### 4. Staff (`user_type = '2'`)
- Apply for leave with supporting documents
- View personal leave history and balance
- View personal calendar (only their own leaves)
- Update profile information

After creating a superuser, log in from `/admin` and set up initial users via the admin interface or the web portal. Assign appropriate user types to enable role-based access.

---

## 📅 Calendar Features

The system includes comprehensive calendar functionality with user-specific views:

### Staff Calendar
- View only your own leave requests
- See leave status (pending, approved, rejected) on calendar dates
- View public holidays and calendar events
- Access via: Sidebar → Calendar

### Admin Calendar
- View all leaves across entire organization
- See all leave statuses (pending, approved, rejected)
- Access via: Sidebar → Calendar

### HR Calendar
- View all approved leaves across organization
- Monitor organization-wide leave patterns
- Access via: Sidebar → Calendar

### Department Head Calendar
- View only leaves from your department staff
- See all leave statuses for department members
- Access via: Sidebar → Department Calendar

**Note:** Each calendar is user-specific - users only see leaves relevant to their role and permissions.

## 🛠 Troubleshooting
- Run `python manage.py collectstatic` if static files do not appear
- Check your browser cache and Django settings if UI looks broken
- Ensure user_type is correctly set (1=Admin, 2=Staff, 3=Department Head, 4=HR)
- Calendar views are role-specific - verify user permissions if calendar appears empty
- See `staffleave/QUICK_START_GUIDE.md` for detailed setup instructions

---

## 🤝 Contributing
Forks & contributions are welcome! Open issues or pull requests for bugs and feature ideas.

---

## 📜 License
This project is intended for educational and internal use. Adapt as required for your organization!

---

## 📚 Additional Documentation
- See `staffleave/QUICK_START_GUIDE.md` for detailed setup and configuration
- See `staffleave/SYSTEM_ENHANCEMENT_SUMMARY.md` for recent system enhancements

## 🤔 Questions?
If you have issues, review the troubleshooting section above or check the additional documentation files in the `staffleave/` directory.
