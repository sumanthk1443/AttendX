# SMTP Setup Guide for AttendX

## Quick Setup (Gmail Recommended)

### Step 1: Create a .env file
Copy the `.env.example` file to `.env` and fill in your email credentials.

```bash
cp .env.example .env
```

### Step 2: Configure Gmail (Easiest Method)

#### Option A: Using Gmail App Password (Recommended for 2FA enabled accounts)

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** on the left sidebar
3. Enable **2-Step Verification** (if not already enabled)
4. Search for "App passwords"
5. Select **Mail** and **Windows Computer** (or your device)
6. Google will generate a 16-character password
7. Copy this password and add to your `.env` file:

```
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16_char_app_password
```

#### Option B: Using Gmail Password (For accounts without 2FA)

1. Go to account settings and ensure "Less secure app access" is enabled
2. Use your regular Gmail password:

```
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_password
```

### Step 3: Update requirements.txt and install python-dotenv

```bash
pip install python-dotenv
# or
pip install -r requirements.txt
```

### Step 4: Create .env file

Create a file named `.env` in the project root (same location as app.py):

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

### Step 5: Restart Flask Application

```bash
python app.py
```

---

## Alternative Email Providers

### Microsoft Outlook / Office 365
```
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=your_email@outlook.com
```

### SendGrid
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your_sendgrid_api_key
MAIL_DEFAULT_SENDER=noreply@yourcompany.com
```

### Mailgun
```
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=postmaster@sandboxXXX.mailgun.org
MAIL_PASSWORD=your_mailgun_password
MAIL_DEFAULT_SENDER=noreply@sandboxXXX.mailgun.org
```

---

## Testing Email Functionality

### Test from Admin Panel
1. Login as admin
2. Go to "Add User"
3. Fill in user details:
   - Name: Test User
   - Email: your_test_email@gmail.com
   - Role: Employee
4. Click "Add User"
5. You should receive an email with login credentials

### Check Logs
If email fails to send, check Flask console output for error messages. Common issues:
- Wrong app password
- Gmail account not allowing less secure apps
- Incorrect email address
- Network/firewall issues

---

## Email Template Customization

Edit `/templates/auth/credentials_email.html` to customize the email appearance.

The following variables are available:
- `{{ name }}` - User's name
- `{{ email }}` - User's email
- `{{ password }}` - Generated temporary password
- `{{ role }}` - User's role (Admin, Manager, HR, Employee)
- `{{ portal }}` - Portal name based on role

---

## Security Notes

⚠️ **Never commit `.env` file to Git!**

The `.env` file is already in `.gitignore`. Always use:
- App Passwords for Gmail (not your actual Gmail password)
- Use environment variables in production
- Change default sender email to no-reply@yourcompany.com

---

## Troubleshooting

### "SMTPAuthenticationError: Invalid credentials"
- Check your app password is correct (should be 16 characters)
- Verify email address matches your Gmail account

### "Connection refused"
- Check firewall settings
- Verify port 587 is not blocked
- Try port 465 with `MAIL_USE_TLS=False` and `MAIL_USE_SSL=True`

### Email not sending but no error
- Check .env file is in correct location
- Verify `load_dotenv()` is called in app.py
- Restart Flask application after changing .env

### Still not working?
1. Check .env file exists in project root
2. Verify all variables are set correctly
3. Restart Flask application
4. Check Flask console for error messages
5. Try sending a test email via Python:

```python
from app import mail, Message
msg = Message(subject='Test', recipients=['your_email@gmail.com'], body='Test')
mail.send(msg)
```
