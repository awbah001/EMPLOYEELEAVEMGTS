# Staff Leave Management System (SLMS)

A professional Django-based web application designed for managing staff leave requests within an organization. This system allows both admins and staff to interact via role-based interfaces and includes a modern, responsive design for an enhanced user experience.

---

## 🚀 Features

- **Role-based Access:** Separate portals for admins and staff
- **Leave Application Workflow:** Staff can apply for leave, admins can view/approve/disapprove
- **User Profiles:** With photo upload and personal details
- **Modern Responsive UI:** Beautiful blue gradient, sidebar navigation, and clean cards
- **Email Authentication:** Custom backend-ready
- **Easy Extension:** Built following Django best-practices

---

## 📁 Project Structure

```
Staff-Leave-MS-Django-Python/
│
├── staffleave/
│   ├── slms/             # Django main project (settings, urls, wsgi, asgi)
│   ├── slmsapp/          # Main application logic (models, views, admin, migrations)
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # HTML templates
│   ├── media/            # User-uploaded profile pics
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

### 4. Apply migrations & create a superuser (admin)
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the development server
```bash
python manage.py runserver
```
Go to http://127.0.0.1:8000/ in your browser.

---

## 🔑 Default Roles & Usage
- **Admin:** Access admin dashboard, add/edit/delete staff, view & approve leave
- **Staff:** Apply for leave, view leave status/history, update profile

After creating a superuser, log in from `/admin` and set up initial staff via the admin interface or the web portal.

---

## 🛠 Troubleshooting
- Run `python manage.py collectstatic` if static files do not appear
- Check your browser cache and Django settings if UI looks broken (see `DESIGN_TROUBLESHOOTING.md`)
- See sample config in `staffleave/` directory for design and deployment advice

---

## 🤝 Contributing
Forks & contributions are welcome! Open issues or pull requests for bugs and feature ideas.

---

## 📜 License
This project is intended for educational and internal use. Adapt as required for your organization!

---

## 🤔 Questions?
If you have issues, review `DESIGN_TROUBLESHOOTING.md` or contact the original author.
