import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from jose import jwt, ExpiredSignatureError

from accounts.models import PasswordResets, User


def send_welcome_email(user, token, type):
    subject = "Welcome to Hoist Cloud"
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


def invite_user_email(user, token, title_data, email_type):
    subject = "Welcome to Hoist Cloud"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/invite.html",
        {
            "user": user,
            "token": token,
            "site": os.getenv("SITE_NAME"),
            "type": email_type,
            "title_data": title_data,
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
    subject = "Welcome to Hoist Cloud"
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
    subject = "Welcome to Hoist Cloud"
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


def user_denied(user, token, type):
    subject = "Welcome to Hoist Cloud"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]

    html_content = render_to_string(
        "emails/user_denied.html",
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


def admin_details(users):
    return {
        "id": users.id,
        "email": users.email,
        "first_name": users.first_name,
        "last_name": users.last_name,
        "role": {
            "id": users.role_id,
            "name": users.role.name,
        }
    }

def property_manager_details(users):
    return {
        "id": users.id,
        "email": users.email,
        "first_name": users.first_name,
        "last_name": users.last_name,
        "phone_number": users.phone_number,
        "company_name": users.company_name,
        "company_address": users.company_address,
        "role": {
            "id": users.role_id,
            "name": users.role.name,
        },
        "subscription": {
            "id": users.subscription_id if users.subscription else "",
            "name": users.subscription.name if users.subscription else "",
            "amount": users.subscription.amount if users.subscription else "",
        }

    }

def operator_details(users):
    return {
                "id": users.id,
                "email": users.email,
                "first_name": users.first_name,
                "last_name": users.last_name,
                "title": {
                    "id": users.title.id,
                    "name": users.title.name,
                },
                "qei_no": users.qei_number,
                "role": {
                    "id": users.role_id,
                    "name": users.role.name,
                },
                "subscription": {
                    "id": users.subscription_id if users.subscription else "",
                    "name": users.subscription.name if users.subscription else "",
                    "amount": users.subscription.amount if users.subscription else "",
                },
                "invited_by": {
                    "id": users.property_id,
                    "name": f"{users.property.first_name} {users.property.last_name}",
                    "email": f"{users.property.email}",
                    "phone_number": users.property.phone_number,
                    "company_name": users.property.company_name,
                    "company_address": users.property.company_address,
                } if users.property else None

            }


def get_user_from_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "refresh":
            return 401, {
                "status": "ERROR",
                "message": "Invalid token type.",
            }

        user_id = payload.get("id")

        if not user_id:
            return 401, {
                "status": "ERROR",
                "message": "Invalid token payload.",
            }

        user = User.objects.filter(id=user_id).first()

        if not user:
            return 400, {
                "status": "ERROR",
                "message": "User not found.",
            }

        return user, payload

    except ExpiredSignatureError:
        return 400, {
            "status": "ERROR",
            "message": "Refresh token expired.",
        }