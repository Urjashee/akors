import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from accounts.models import PasswordResets

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

def invite_user_email(user, token, type):
    subject = "Welcome to Akors 🎉"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/invite.html",
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

def create_password_email(user, token, type):
    subject = "Welcome to Akors 🎉"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/set_password.html",
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


def process_password_setup(token, password, qei_number=None):
    reset = (
        PasswordResets.objects
        .filter(token=token, active=True)
        .select_related("user")
        .order_by("-id")
        .first()
    )

    if not reset:
        return None, "Invalid or expired token."

    # deactivate token
    reset.active = False
    reset.save(update_fields=["active"])

    user = reset.user
    user.set_password(password)
    user.is_active = True
    user.is_approved = True
    user.email_verified_at = timezone.now()

    if qei_number:
        user.qei_number = qei_number

    update_fields = [
        "password",
        "email_verified_at",
        "is_active",
        "is_approved",
    ]

    if qei_number:
        update_fields.append("qei_number")

    user.save(update_fields=update_fields)

    return user, None
