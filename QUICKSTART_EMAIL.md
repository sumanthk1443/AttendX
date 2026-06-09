# 🚀 SMTP Configuration - Quick Start

## Current Status ✅
Your Flask app is ready to send emails! Here's what's been set up:

- ✅ Flask-Mail installed
- ✅ Email function created (`send_credentials_email`)
- ✅ Email template designed (`credentials_email.html`)
- ✅ Environment variable system configured
- ✅ Admin user creation integrated with email sending

---

## Next Steps: Configure Your Email

### ⚡ Super Quick Setup (5 minutes)

#### 1. Open `.env` file in your project root
Located at: `c:\Users\ADMIN\Desktop\Python\rbac_attendance\.env`

#### 2. Add your Gmail credentials

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

#### 3. Get your App Password (Recommended)

**For Gmail accounts with 2-Factor Authentication:**

1. Go to https://myaccount.google.com/
2. Click "Security" on the left
3. Scroll to "App passwords" (requires 2FA enabled)
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character password
6. Paste it in `.env` file as `MAIL_PASSWORD`

**Without 2FA:**
- Just use your regular Gmail password

#### 4. Restart Flask
Stop and restart your Flask application for changes to take effect.

---

## ✅ Test It!

1. Login to your app as Admin
2. Go to "Admin Dashboard" → "Add User"
3. Fill in:
   - Name: `Test User`
   - Email: `your-test-email@gmail.com`
   - Role: `Employee`
4. Click "Add User"
5. Check your email inbox (and spam folder)

You should receive a beautiful email with login credentials! 📧

---

## Files Modified

- **app.py** - Now reads from `.env` file
- **requirements.txt** - Added `python-dotenv`
- **.env** - Configuration file (create & update with your credentials)
- **templates/auth/credentials_email.html** - Updated template with new fonts
- **.env.example** - Template reference for `.env`

---

## 📧 Email Content Includes:
✓ User's role  
✓ Temporary password (securely generated)  
✓ Portal name  
✓ Email address  
✓ Security reminder  
✓ Quick start guide  
✓ Login link

---

## Troubleshooting

### ❌ "Email not sent" appears but no error?
- Make sure you restarted Flask after updating `.env`
- Verify `.env` file exists in project root (same location as `app.py`)

### ❌ "SMTPAuthenticationError"?
- Wrong Gmail App Password
- Make sure you used the 16-char generated password, not your Gmail password
- Verify email address is correct

### ❌ Still not working?
1. Check `.env` file is correctly formatted:
   ```
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```
   (No quotes needed)

2. Restart Flask completely
3. Try a test email from Python:
   ```python
   from app import mail, Message
   msg = Message('Test Subject', recipients=['your-email@gmail.com'], body='Test Body')
   mail.send(msg)
   ```

---

## Security Checklist ✅

- [ ] `.env` file created with your credentials
- [ ] Using Gmail App Password (not regular password)
- [ ] `.env` is NOT committed to Git (already in `.gitignore`)
- [ ] `MAIL_DEFAULT_SENDER` is set correctly
- [ ] Flask restarted after `.env` changes

---

## Alternative Email Services

### Outlook/Office 365
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USERNAME=your_email@outlook.com
MAIL_PASSWORD=your_password
```

### SendGrid
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your_api_key_here
```

See **SMTP_SETUP.md** for more details on alternative providers.

---

## 📞 Need Help?

1. Check Flask console output for errors
2. Review SMTP_SETUP.md for detailed guide
3. Verify all `.env` variables are set
4. Restart Flask application

Happy emailing! 🎉
