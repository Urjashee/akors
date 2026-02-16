import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user, token, type):
    subject = "Welcome to Akors 🎉"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/welcome.html",
        {
            "user": user,
            "token": token,
            "site": os.getenv("SITE_NAME"),
            "type": type
        }
    )

    email = EmailMultiAlternatives(subject, "", from_email, to)
    email.attach_alternative(html_content, "text/html")
    sent_count = email.send()

    return sent_count

def send_reset_email(user, token, type):
    subject = "Mail from Akors"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/forgot_password.html",
        {
            "user": user,
            "token": token,
            "site": os.getenv("SITE_NAME"),
            "type": type
        }
    )

    email = EmailMultiAlternatives(subject, "", from_email, to)
    email.attach_alternative(html_content, "text/html")
    sent_count = email.send()

    return sent_count


def operator_sign_up_email(user, token, type):
    subject = "Welcome to Akors 🎉"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/operator_sign_up.html",
        {
            "user": user,
            "token": token,
            "site": os.getenv("SITE_NAME"),
            "type": type
        }
    )

    email = EmailMultiAlternatives(subject, "", from_email, to)
    email.attach_alternative(html_content, "text/html")
    sent_count = email.send()

    return sent_count
