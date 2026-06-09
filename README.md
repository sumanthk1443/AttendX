# 🏢 AttendX — RBAC Attendance Portal

A full Role-Based Access Control (RBAC) attendance management system built with Flask.

## Roles & Access

| Role     | Login Page           | What they can do                              |
|----------|----------------------|-----------------------------------------------|
| Admin    | `/admin/login`       | Add users, assign roles, view all attendance  |
| Employee | `/login`             | Check in/out, view own attendance history     |
| Manager  | `/login`             | View team presence & attendance logs          |
| HR       | `/login`             | View all staff, generate attendance reports   |

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Email (Gmail)
Edit `app.py` and update:
```python
app.config['MAIL_USERNAME'] = 'your_gmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'   # Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'your_gmail@gmail.com'
```
> To get a Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords

### 3. Run the app
```bash
python app.py
```

### 4. Default Admin Credentials
```
URL:      http://localhost:5000/admin/login
Email:    admin@attendx.com
Password: Admin@1234
```

## Flow

```
Admin logs in
  → Opens Admin Dashboard
  → Clicks "Add New User"
  → Fills: Name, Email, Department, Role (Employee / Manager / HR)
  → System generates random password
  → System sends email with credentials
  → New user logs in at /login
  → Redirected to their role-specific portal
```

## Project Structure
```
rbac_attendance/
├── app.py                          # Flask app + routes
├── requirements.txt
└── templates/
    ├── base.html                   # Shared navbar + styles
    ├── auth/
    │   ├── login.html              # User login
    │   ├── admin_login.html        # Admin-specific login
    │   └── credentials_email.html  # Email template
    ├── admin/
    │   ├── dashboard.html
    │   ├── add_user.html
    │   └── attendance.html
    ├── employee/
    │   └── dashboard.html
    ├── manager/
    │   ├── dashboard.html
    │   └── team_attendance.html
    └── hr/
        ├── dashboard.html
        └── reports.html
```
