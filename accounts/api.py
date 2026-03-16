import secrets
from datetime import timedelta

from django.utils import timezone
from ninja import Router
from django.db import transaction
from django.db.models import F

from ninja import Query

from .auth_roles_middleware import SuperAdminAuth, PropertyManagerAuth
from .jwt import create_access_token, create_refresh_token
from .schemas import SuccessSchema, ErrorSchema, RegisterSchema, VerifyEmailSchema, EmailSchema, LoginSchema, \
    UserFilterSchema, CreatePasswordSchema, InvitedUsers, SetupAccount, EditPropertyManager
from .models import User, PasswordResets, Role, Title
from .services import send_welcome_email, send_reset_email, operator_sign_up_email, create_password_email, \
    invite_user_email, process_password_setup
from .constants import WELCOME_EMAIL, FORGOT_PASSWORD_EMAIL, OPERATOR_SIGN_UP_EMAIL, CREATE_PASSWORD_EMAIL, \
    INVITE_EMAIL, PROPERTY_MANAGER

router = Router(tags=["accounts"])


@router.post(
    "/operator/register",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
)
def operator_register(request, payload: RegisterSchema):
    token = secrets.token_urlsafe(32)
    role = Role.objects.get(id=3)
    title_data = Title.objects.get(id=payload.title)
    try:
        with transaction.atomic():
            existing_user = User.objects.filter(email=payload.email).first()
            if existing_user:
                if existing_user.email_verified_at is None:
                    existing_user.set_password(payload.password)
                    existing_user.first_name = payload.first_name
                    existing_user.last_name = payload.last_name
                    existing_user.title = title_data
                    existing_user.qei_number = payload.qei_number
                    existing_user.role = role
                    existing_user.save()
                    password_resets = PasswordResets.objects.create(
                        email=existing_user.email,
                        token=token,
                        type=WELCOME_EMAIL,
                        user=existing_user
                    )
                    if not password_resets:
                        return 400, {
                            "status": "ERROR",
                            "message": "Could not create password token. Please try again later.",
                        }
                    email_sent = send_welcome_email(existing_user, token, type=WELCOME_EMAIL)
                    if not email_sent == 1:
                        return 400, {
                            "status": "ERROR",
                            "message": "Could not send email. Please try again later.",
                        }
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
                    "status": "ERROR",
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
                    "message": "Could not register user!",
                }
            user.set_password(payload.password)
            user.save()
            password_resets = PasswordResets.objects.create(
                email=user.email,
                token=token,
                type=WELCOME_EMAIL,
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

    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full stacktrace in console/logs
        return 400, {
            "status": "ERROR",
            "message": str(e),
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
    "/property_manager/register",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
)
def property_manager_register(request, payload: RegisterSchema):
    token = secrets.token_urlsafe(32)
    role = Role.objects.get(id=2)
    try:
        with transaction.atomic():
            existing_user = User.objects.filter(email=payload.email).first()
            if existing_user:
                if existing_user.email_verified_at is None:
                    existing_user.first_name = payload.first_name
                    existing_user.last_name = payload.last_name
                    existing_user.company_name = payload.company_name
                    existing_user.company_address = payload.company_address
                    existing_user.phone_number = payload.phone_number
                    existing_user.role = role
                    existing_user.save()

                    email_sent = operator_sign_up_email(existing_user, token, type=OPERATOR_SIGN_UP_EMAIL)
                    if not email_sent == 1:
                        return 400, {
                            "status": "ERROR",
                            "message": "Could not send email. Please try again later.",
                        }
                    return 200, {
                        "status": "SUCCESS",
                        "message": "Successfully created operator account.",
                        "data": {
                            "email": existing_user.email,
                            "first_name": existing_user.first_name,
                            "last_name": existing_user.last_name,
                        },
                    }
                return 400, {
                    "status": "ERROR",
                    "message": "Email already registered",
                }

            user = User.objects.create(
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                company_name=payload.company_name,
                company_address=payload.company_address,
                phone_number=payload.phone_number,
                role=role,
            )
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not register user!",
                }
            user.save()

            email_sent = operator_sign_up_email(user, token, type=OPERATOR_SIGN_UP_EMAIL)
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


    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full stacktrace in console/logs
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully created operator account.",
        "data": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }


@router.post(
    "/verify",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
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
            user.is_active = True
            user.is_approved = True
            user.email_verified_at = timezone.now()
            user.save(update_fields=["email_verified_at", "is_active", "is_approved"])

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": "Could not verify email.",
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Email verified successfully",
        "data": None
    }


@router.post(
    "/forgot-password",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
)
def forgot_password_request(request, payload: EmailSchema):
    token = secrets.token_urlsafe(32)
    try:
        with transaction.atomic():
            user = User.objects.get(email=payload.email)
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }

            if user.email_verified_at is None:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }
            five_minutes_ago = timezone.now() - timedelta(minutes=1)

            recent_request_exists = PasswordResets.objects.filter(
                user=user,
                type=2,
                created_at__gte=five_minutes_ago,
                active=True
            ).exists()

            if recent_request_exists:
                return 400, {
                    "status": "ERROR",
                    "message": "A password reset email was already sent recently. Please wait 5 minutes.",
                }

            password_resets = PasswordResets.objects.create(
                email=payload.email,
                token=token,
                type=2,
                user=user
            )
            if not password_resets:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not create password reset token. Please try again later.",
                }

            email_sent = send_reset_email(user, token, type=FORGOT_PASSWORD_EMAIL)
            if not email_sent == 1:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not send email. Please try again later.",
                }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": "Could not verify email.",
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Password reset request sent successfully.",
        "data": None
    }


@router.post(
    "/reset-password",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
)
def reset_password_request(request, payload: VerifyEmailSchema):
    try:
        with transaction.atomic():
            resent_request_exists = PasswordResets.objects.get(
                token=payload.token,
                type=2,
                active=True
            )
            user = User.objects.get(email=resent_request_exists.email)
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }

            if user.check_password(payload.password):
                return 400, {
                    "status": "ERROR",
                    "message": "Password cannot be same as your previous one.",
                }

            user.set_password(payload.password)
            user.save()

            if not resent_request_exists:
                return 400, {
                    "status": "ERROR",
                    "message": "No associated password reset token. Please try again later.",
                }
            resent_request_exists.active = False
            resent_request_exists.save(update_fields=["active"])

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": "Could not verify email.",
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Password reset successfully.",
        "data": None
    }


@router.post(
    "/login",
    auth=None,
    response={ 200: SuccessSchema, 400: ErrorSchema },
)
def login(request, payload: LoginSchema):
    try:
        with transaction.atomic():

            user = User.objects.filter(email=payload.email, is_active=True).first()
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }
            if not user.check_password(payload.password):
                return 400, {
                    "status": "ERROR",
                    "message": "Invalid email or password.",
                }

            if user.email_verified_at is None:
                return 400, {
                    "status": "ERROR",
                    "message": "Please verify your email first.",
                }


    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),

        }

    return 200, {
        "status": "SUCCESS",
        "message": "Login successful.",
        "data": {
            "access_token": create_access_token(user),
            "refresh_token": create_refresh_token(user)
        }
    }


@router.post(
    "/create-password",
    auth=None,
    response={200: SuccessSchema, 400: ErrorSchema},
)
def create_password(request, payload: CreatePasswordSchema):
    try:
        with transaction.atomic():
            user, error = process_password_setup(
                payload.token,
                payload.password
            )

            if error:
                return 400, {"status": "ERROR", "message": error}

            return 200, {
                "status": "SUCCESS",
                "message": "Successfully approved property manager.",
                "data": None
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


#  *************************** ADMIN **************************************

@router.get(
    "/admin/users",
    auth=SuperAdminAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def admin_user_list(request, filters: UserFilterSchema = Query(...)):
    try:
        users = User.objects.select_related("role").all()

        if filters.status:

            if filters.status == "verified_operator":
                users = users.filter(
                    email_verified_at__isnull=False,
                    role_id=3
                )

            elif filters.status == "verified_property_manager":
                users = users.filter(
                    email_verified_at__isnull=False,
                    is_approved=True,
                    role_id=2
                )

            elif filters.status == "pending_property_manager":
                users = users.filter(
                    email_verified_at__isnull=True,
                    is_approved=False,
                    role_id=2
                )

        users = users.annotate(
            role_name=F("role__name"),
            subscription_name=F("subscription__name")
        )

        return 200, {
            "status": "SUCCESS",
            "message": "Users fetched successfully.",
            "data": list(users.values(
                "id",
                "email",
                "first_name",
                "last_name",
                "email_verified_at",
                "is_active",
                "role_id",
                "role__name",
                "subscription__name"
            ))
        }

    except Exception:
        return 400, {
            "status": "ERROR",
            "message": "Could not fetch users.",
        }


@router.post(
    "/admin/user-approve/{user_id}",
    auth=SuperAdminAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def approve_user(request, user_id: int):
    if request.user.role.name != "Super admin":
        return 403, {
            "status": "Unauthorized",
            "message": "Permission denied. Super admin only.",
        }

    token = secrets.token_urlsafe(32)

    try:
        with transaction.atomic():

            user = User.objects.filter(id=user_id, role_id=2).first()
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }
            user.is_approved = True
            user.save(update_fields=["is_approved"])
            password_resets = PasswordResets.objects.create(
                email=user.email,
                token=token,
                type=CREATE_PASSWORD_EMAIL,
                user=user
            )
            if not password_resets:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not create email token. Please try again later.",
                }
            email_sent = create_password_email(user, token, type=CREATE_PASSWORD_EMAIL)
            if not email_sent == 1:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not send email. Property manager approved.",
                }
            return 200, {
                "status": "SUCCESS",
                "message": "Successfully approved property manager.",
                "data": None
            }

    except Exception:
        return 400, {
            "status": "ERROR",
            "message": "Could not fetch users.",
        }


@router.patch(
    "/admin/user-toggle/{user_id}",
    auth=SuperAdminAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def approve_user(request, user_id: int):
    if request.user.role.name != "Super admin":
        return 403, {
            "status": "Unauthorized",
            "message": "Permission denied. Super admin only.",
        }

    try:
        with transaction.atomic():

            user = User.objects.filter(id=user_id, is_approved=True).first()
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }
            if user.is_active:
                user.is_active = False
            else:
                user.is_active = True
            user.save(update_fields=["is_active"])

            return 200, {
                "status": "SUCCESS",
                "message": "Successfully updated user status.",
                "data": None
            }

    except Exception:
        return 400, {
            "status": "ERROR",
            "message": "Could not fetch users.",
        }


#  *************************** PROPERTY MANAGER **************************************


@router.get(
    "/property-manager/profile",
    auth=PropertyManagerAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def property_manager_get_profile(request):
    try:
        users = User.objects.filter(email=request.user.email).first()
        if not users:
            return 400, {
                "status": "ERROR",
                "message": "No user found.",
            }

        if users.role.id is not PROPERTY_MANAGER:
            return 403, {
                "status": "ERROR",
                "message": "Permission denied. Property manager only.",
            }

        return 200, {
            "status": "SUCCESS",
            "message": "Users fetched successfully.",
            "data": {
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
        }

    except Exception:
        return 400, {
            "status": "ERROR",
            "message": "Could not fetch users.",
        }


@router.post(
    "/property-manager/profile/edit",
    auth=PropertyManagerAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def property_manager_edit_profile(request, payload: EditPropertyManager):
    try:
        with transaction.atomic():
            user = User.objects.filter(email=request.user.email).first()
            print(user)
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "No user found.",
                }

            if user.role.id is not PROPERTY_MANAGER:
                return 403, {
                    "status": "ERROR",
                    "message": "Permission denied. Property manager only.",
                }

            user.first_name = payload.first_name
            user.last_name = payload.last_name
            user.company_name = payload.company_name
            user.company_address = payload.company_address
            user.phone_number = payload.phone_number
            user.save(update_fields=["first_name", "last_name", "company_name", "company_address", "phone_number"])

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": f"Could not fetch users. {str(e)}",
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully updated property manager.",
        "data": None
    }

@router.post(
    "/property-manager/invite-users",
    auth=PropertyManagerAuth(),
    response={ 200: SuccessSchema, 400: ErrorSchema, 403: ErrorSchema },
)
def property_manager_invite_user(request, payload: InvitedUsers):
    token = secrets.token_urlsafe(32)
    role = Role.objects.get(id=3)
    title_data = Title.objects.get(id=payload.title)
    try:
        with transaction.atomic():
            existing_user = User.objects.filter(email=payload.email).first()
            if existing_user:
                return 400, {
                    "status": "ERROR",
                    "message": "User with this email already exists.",
                }

            user = User.objects.create(
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                title=title_data,
                role=role,
                property=request.user,
            )
            if not user:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not invite user!",
                }

            password_resets = PasswordResets.objects.create(
                email=user.email,
                token=token,
                type=INVITE_EMAIL,
                user=user
            )

            if not password_resets:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not create password reset token. Please try again later.",
                }
            email_sent = invite_user_email(user, token, type=INVITE_EMAIL)
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

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }

    return 200, {
        "status": "SUCCESS",
        "message": "Successfully invited operator account.",
        "data": None
    }


@router.post(
    "/setup",
    auth=None,
    response={200: SuccessSchema, 400: ErrorSchema},
)
def property_manager_setup_account(request, payload: SetupAccount):
    try:
        with transaction.atomic():
            user, error = process_password_setup(
                payload.token,
                payload.password,
                payload.qei_number
            )

            if error:
                return 400, {"status": "ERROR", "message": error}

            return 200, {
                "status": "SUCCESS",
                "message": "Operator account setup successfully.",
                "data": None
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}
