import secrets

from django.utils import timezone
from ninja import Router
from .schemas import UserOutSchema, ErrorSchema, RegisterSchema, VerifyEmailSchema
from .models import User, PasswordResets, Role, Title
from .services import send_welcome_email
from django.db import transaction

router = Router(tags=["accounts"])


@router.post(
    "/operator/register",
    auth=None,
    response={
        200: UserOutSchema,
        400: ErrorSchema,
    },
)
def register(request, payload: RegisterSchema):
    token = secrets.token_urlsafe(32)
    role = Role.objects.get(id=3)
    title_data = Title.objects.get(id=payload.title)
    try:
        with transaction.atomic():
            existing_user = User.objects.get(email=payload.email)
            if existing_user:
                if existing_user.email_verified_at is None:
                    existing_user.password = payload.password
                    existing_user.first_name = payload.first_name
                    existing_user.last_name = payload.last_name
                    existing_user.title = title_data
                    existing_user.qei_number = payload.qei_number
                    existing_user.role = role
                    existing_user.save()
                    password_resets = PasswordResets.objects.create(
                        email=existing_user.email,
                        token=token,
                        type=1,
                        user=existing_user
                    )
                    if not password_resets:
                        return 400, {
                            "status": "ERROR",
                            "message": "Could not create password reset token. Please try again later.",
                        }
                    send_welcome_email(existing_user, token, type=1)
                    return 200, {
                        "status": "SUCCESS",
                        "message": "Successfully created operator account.",
                        "data": {
                            "email": existing_user.email,
                            "first_name": existing_user.first_name,
                            "last_name": existing_user.last_name,
                            "qei_number": existing_user.qei_number,
                        },
                    }
                return 400, {
                    "status": "EMAIL_EXISTS",
                    "message": "Email already registered",
                }

            user = User.objects.create(
                email=payload.email,
                password=payload.password,
                first_name=payload.first_name,
                last_name=payload.last_name,
                title=title_data,
                qei_number=payload.qei_number,
                role=role,
            )
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not register user 2!",
                }
            user.set_password(payload.password)
            user.save()
            password_resets = PasswordResets.objects.create(
                email=user.email,
                token=token,
                type=1,
                user=user
            )
            if not password_resets:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not create password reset token. Please try again later.",
                }

            email_sent = send_welcome_email(user, token, type=1)
            if not email_sent == 1:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not send email. Please try again later.",
                }
    except Role.DoesNotExist:
        return 400, {
            "status": "ERROR",
            "message": "Invalid role.",
        }

    except Title.DoesNotExist:
        return 400, {
            "status": "ERROR",
            "message": "Invalid title.",
        }

    except Exception:
        # Any error here → full rollback
        return 400, {
            "status": "ERROR",
            "message": "Registration failed. Please try again.",
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully created operator account.",
        "data": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "qei_number": user.qei_number,
        },
    }


@router.post(
    "/verify",
    auth=None,
    response={
        200: UserOutSchema,
        400: ErrorSchema,
    },
)
def verify_email(request, payload: VerifyEmailSchema):
    try:
        with transaction.atomic():
            reset = (
                PasswordResets.objects
                .filter(token=payload.token, active=True)
                .select_related("user")
                .order_by("-id")
                .first()
            )

            if not reset:
                return 400, {
                    "status": "ERROR",
                    "message": "Invalid or expired token.",
                }

            # deactivate token
            reset.active = False
            reset.save(update_fields=["active"])

            # verify user
            user = reset.user
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at"])

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": "Could not verify email.",
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Email verified successfully",
    }
