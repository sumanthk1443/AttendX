from flask_mail import Message
from app import mail
from flask import render_template

def send_credentials_email(user_email, user_name, password, role):

    msg = Message(
        subject="Your Account Has Been Created",
        recipients=[user_email]
    )

    msg.html = render_template(
        "auth/credentials_email.html",
        name=user_name,
        email=user_email,
        password=password,
        role=role
    )

    mail.send(msg)