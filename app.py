from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
import secrets
import string
import os
import smtplib
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables from the project root .env file
base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'rbac-attendance-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = \
'mysql+pymysql://root:root@localhost/admins'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Mail config (reads from .env file)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
mail_username = os.getenv('MAIL_USERNAME', '')
mail_default_sender = os.getenv('MAIL_DEFAULT_SENDER', '')
if not mail_username and mail_default_sender:
    mail_username = mail_default_sender
if '@' not in mail_username and '@' in mail_default_sender:
    mail_username = mail_default_sender
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender or mail_username

if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
    app.logger.warning('MAIL_USERNAME or MAIL_PASSWORD is not set. SMTP email sending will fail.')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ─── Enums ────────────────────────────────────────────────────────────────────
class RoleEnum(str, Enum):
    ADMIN    = 'admin'
    EMPLOYEE = 'employee'
    MANAGER  = 'manager'
    HR       = 'hr'


# ─── Models ───────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    department    = db.Column(db.String(100))
    role          = db.Column(db.String(20), nullable=False, default=RoleEnum.EMPLOYEE)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    attendances   = db.relationship('Attendance', backref='user', lazy=True)

    # Flask-Login interface
    @property
    def is_authenticated(self): return True
    @property
    def is_anonymous(self):    return False
    def get_id(self):          return str(self.id)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date       = db.Column(db.Date, default=date.today)
    check_in   = db.Column(db.DateTime)
    check_out  = db.Column(db.DateTime)
    status     = db.Column(db.String(20), default='Present')  # Present / Absent / Leave
    notes      = db.Column(db.String(255))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Helpers ──────────────────────────────────────────────────────────────────
def generate_password(length=10):
    chars = string.ascii_letters + string.digits + '!@#$'
    return ''.join(secrets.choice(chars) for _ in range(length))


def send_credentials_email(name, email, password, role):
    role_url_map = {
        'employee': 'Employee Portal',
        'manager':  'Manager Portal',
        'hr':       'HR Portal',
    }
    portal = role_url_map.get(role, 'Company Portal')
    try:
        msg = Message(
            subject='🎉 Your Account Has Been Created – AttendX',
            recipients=[email]
        )
        msg.html = render_template(
            'auth/credentials_email.html',
            name=name, email=email, password=password,
            role=role.capitalize(), portal=portal
        )
        mail.send(msg)
        return True, None
    except smtplib.SMTPAuthenticationError as e:
        error_message = 'SMTP authentication failed. Check MAIL_USERNAME and MAIL_PASSWORD, and use a valid Gmail app password if using Gmail.'
        app.logger.error('Mail auth error: %s', str(e))
        return False, error_message
    except Exception as e:
        error_message = str(e)
        app.logger.error('Mail error: %s', error_message)
        return False, error_message


def generate_otp(length=6):
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def send_otp_email(name, email, otp):
    try:
        msg = Message(
            subject='🔐 Your AttendX Password Reset OTP',
            recipients=[email]
        )
        msg.body = (
            f'Hello {name},\n\n'
            f'Your password reset OTP is: {otp}\n\n'
            'Enter this OTP on the AttendX reset page to verify your email and choose a new password.\n\n'
            'If you did not request a password reset, please ignore this message.\n\n'
            'Thanks,\nAttendX Team'
        )
        mail.send(msg)
        return True, None
    except smtplib.SMTPAuthenticationError as e:
        error_message = 'SMTP authentication failed. Check MAIL_USERNAME and MAIL_PASSWORD, and use a valid Gmail app password if using Gmail.'
        app.logger.error('OTP mail auth error: %s', str(e))
        return False, error_message
    except Exception as e:
        error_message = str(e)
        app.logger.error('OTP mail error: %s', error_message)
        return False, error_message


def role_redirect(user):
    """Redirect user to their role-specific dashboard."""
    if user.role == RoleEnum.ADMIN:
        return redirect(url_for('admin_dashboard'))
    elif user.role == RoleEnum.MANAGER:
        return redirect(url_for('manager_dashboard'))
    elif user.role == RoleEnum.HR:
        return redirect(url_for('hr_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))


# ─── Auth Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if current_user.is_authenticated:
        return role_redirect(current_user)
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return role_redirect(current_user)
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return role_redirect(user)
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return role_redirect(current_user)

    stage = session.get('forgot_stage', 'email')
    email = session.get('forgot_email', '')

    if request.method == 'POST':
        action = request.form.get('action', 'send_otp')

        if action == 'send_otp':
            email = request.form.get('email', '').strip().lower()
            if not email:
                flash('Please enter your email address.', 'warning')
                return render_template('auth/forgot_password.html', stage='email')

            user = User.query.filter_by(email=email).first()
            if not user or not user.is_active:
                flash('No active account found for that email address.', 'danger')
                return render_template('auth/forgot_password.html', stage='email')

            otp = generate_otp()
            session['forgot_email'] = email
            session['forgot_otp'] = otp
            session['forgot_stage'] = 'verify'

            mail_sent, mail_error = send_otp_email(user.name, email, otp)
            if mail_sent:
                flash('OTP sent to your email. Enter the code below to verify.', 'success')
            else:
                flash(f'Unable to send OTP email. {mail_error}', 'danger')
            return render_template('auth/forgot_password.html', stage='verify', email=email)

        elif action == 'verify_otp':
            entered_otp = request.form.get('otp', '').strip()
            if not entered_otp:
                flash('Enter the OTP sent to your email.', 'warning')
                return render_template('auth/forgot_password.html', stage='verify', email=email)

            if entered_otp != session.get('forgot_otp'):
                flash('OTP is incorrect. Please try again.', 'danger')
                return render_template('auth/forgot_password.html', stage='verify', email=email)

            session['forgot_stage'] = 'reset'
            flash('OTP verified. You can now set a new password.', 'success')
            return render_template('auth/forgot_password.html', stage='reset', email=email)

        elif action == 'reset_password':
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            if not new_password or not confirm_password:
                flash('Please enter and confirm your new password.', 'warning')
                return render_template('auth/forgot_password.html', stage='reset', email=email)

            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'danger')
                return render_template('auth/forgot_password.html', stage='reset', email=email)

            if session.get('forgot_stage') != 'reset' or not session.get('forgot_email'):
                flash('OTP verification is required before resetting your password.', 'danger')
                return redirect(url_for('forgot_password'))

            user = User.query.filter_by(email=session.get('forgot_email')).first()
            if not user:
                flash('No account found for your email.', 'danger')
                return redirect(url_for('forgot_password'))

            user.set_password(new_password)
            db.session.commit()
            session.pop('forgot_stage', None)
            session.pop('forgot_email', None)
            session.pop('forgot_otp', None)
            flash('Your password has been updated. Please log in with your new password.', 'success')
            return redirect(url_for('login'))

    return render_template('auth/forgot_password.html', stage=stage, email=email)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == RoleEnum.ADMIN:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email, role=RoleEnum.ADMIN).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Admin logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('auth/admin_login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ─── Admin Routes ─────────────────────────────────────────────────────────────
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != RoleEnum.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    users      = User.query.filter(User.role != RoleEnum.ADMIN).all()
    stats = {
        'total':    len(users),
        'employee': sum(1 for u in users if u.role == RoleEnum.EMPLOYEE),
        'manager':  sum(1 for u in users if u.role == RoleEnum.MANAGER),
        'hr':       sum(1 for u in users if u.role == RoleEnum.HR),
    }
    today_att = Attendance.query.filter_by(date=date.today()).count()
    return render_template('admin/dashboard.html', users=users, stats=stats, today_att=today_att)


@app.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if current_user.role != RoleEnum.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        name       = request.form.get('name', '').strip()
        email      = request.form.get('email', '').strip().lower()
        department = request.form.get('department', '').strip()
        role       = request.form.get('role', 'employee')

        if not name or not email or not role:
            flash('All fields are required.', 'warning')
            return render_template('admin/add_user.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/add_user.html')

        raw_password = generate_password()
        user = User(name=name, email=email, department=department, role=role)
        user.set_password(raw_password)
        db.session.add(user)
        db.session.commit()

        mail_sent, mail_error = send_credentials_email(name, email, raw_password, role)
        if mail_sent:
            flash(f'✅ User {name} added and credentials sent to {email}.', 'success')
        else:
            flash(
                f'✅ User {name} added. Email could not be sent. Temp Password: {raw_password}. '
                f'Check MAIL_USERNAME/MAIL_PASSWORD and Gmail app password settings. Error: {mail_error}',
                'warning'
            )

        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_user.html')


@app.route('/admin/toggle-user/<int:user_id>', methods=['POST'])
@login_required
def toggle_user(user_id):
    if current_user.role != RoleEnum.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.name} has been {status}.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != RoleEnum.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} deleted.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/attendance')
@login_required
def admin_attendance():
    if current_user.role != RoleEnum.ADMIN:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    records = db.session.query(Attendance, User).join(User).order_by(Attendance.date.desc()).all()
    return render_template('admin/attendance.html', records=records)


# ─── Employee Routes ───────────────────────────────────────────────────────────
@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    if current_user.role != RoleEnum.EMPLOYEE:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    today_record = Attendance.query.filter_by(user_id=current_user.id, date=date.today()).first()
    history = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.date.desc()).limit(10).all()
    return render_template('employee/dashboard.html', today_record=today_record, history=history)


@app.route('/employee/checkin')
@login_required
def employee_checkin():
    if current_user.role != RoleEnum.EMPLOYEE:
        return redirect(url_for('login'))
    today_record = Attendance.query.filter_by(user_id=current_user.id, date=date.today()).first()
    if today_record:
        flash('You already checked in today.', 'warning')
    else:
        record = Attendance(user_id=current_user.id, check_in=datetime.now(), status='Present')
        db.session.add(record)
        db.session.commit()
        flash('✅ Check-in recorded!', 'success')
    return redirect(url_for('employee_dashboard'))


@app.route('/employee/checkout')
@login_required
def employee_checkout():
    if current_user.role != RoleEnum.EMPLOYEE:
        return redirect(url_for('login'))
    today_record = Attendance.query.filter_by(user_id=current_user.id, date=date.today()).first()
    if not today_record:
        flash('Please check in first.', 'warning')
    elif today_record.check_out:
        flash('You already checked out today.', 'warning')
    else:
        today_record.check_out = datetime.now()
        db.session.commit()
        flash('✅ Check-out recorded!', 'success')
    return redirect(url_for('employee_dashboard'))


# ─── Manager Routes ────────────────────────────────────────────────────────────
@app.route('/manager/dashboard')
@login_required
def manager_dashboard():
    if current_user.role != RoleEnum.MANAGER:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    employees  = User.query.filter_by(role=RoleEnum.EMPLOYEE, is_active=True).all()
    today_att  = Attendance.query.filter_by(date=date.today()).all()
    present_ids = {a.user_id for a in today_att if a.status == 'Present'}
    return render_template('manager/dashboard.html', employees=employees,
                           today_att=today_att, present_ids=present_ids)


@app.route('/manager/team-attendance')
@login_required
def manager_team_attendance():
    if current_user.role != RoleEnum.MANAGER:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    records = db.session.query(Attendance, User).join(User).filter(
        User.role == RoleEnum.EMPLOYEE
    ).order_by(Attendance.date.desc()).all()
    return render_template('manager/team_attendance.html', records=records)


# ─── HR Routes ─────────────────────────────────────────────────────────────────
@app.route('/hr/dashboard')
@login_required
def hr_dashboard():
    if current_user.role != RoleEnum.HR:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    all_users = User.query.filter(User.role != RoleEnum.ADMIN).all()
    stats = {
        'total':    len(all_users),
        'employee': sum(1 for u in all_users if u.role == RoleEnum.EMPLOYEE),
        'manager':  sum(1 for u in all_users if u.role == RoleEnum.MANAGER),
        'hr':       sum(1 for u in all_users if u.role == RoleEnum.HR),
        'active':   sum(1 for u in all_users if u.is_active),
    }
    return render_template('hr/dashboard.html', all_users=all_users, stats=stats)


@app.route('/hr/reports')
@login_required
def hr_reports():
    if current_user.role != RoleEnum.HR:
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    records = db.session.query(Attendance, User).join(User).order_by(Attendance.date.desc()).limit(50).all()
    return render_template('hr/reports.html', records=records)

# ─── DB Init ──────────────────────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        if not User.query.filter_by(role=RoleEnum.ADMIN).first():
            admin = User(
                name='Super Admin',
                email='admin@attendx.com',
                role=RoleEnum.ADMIN,
                department='Administration'
            )

            admin.set_password('12345')

            db.session.add(admin)
            db.session.commit()

            print("✅ Default admin created: admin@attendx.com / 12345")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)