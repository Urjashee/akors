from datetime import datetime, timedelta
from jose import jwt
from django.conf import settings

def create_access_token(user: any):
    payload = {
        "id": user.id,
        "email": str(user.email),
        "first_name": str(user.first_name),
        "last_name": str(user.last_name),
        "is_subscribed": str(user.is_subscribed),
        "subscription": {
            "id": user.subscription.id if user.subscription else "",
            "name": str(user.subscription.name) if user.subscription else "",
        },

        "role": {
            "id": user.role.id if user.role else "",
            "name": str(user.role) if user.role else ""
        },
        "type": "access",
        "exp": datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        "invited_by": user.property_id if user.property_id else None,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user: any):
    payload = {
        "id": user.id,
        "email": str(user.email),
        "first_name": str(user.first_name),
        "last_name": str(user.last_name),
        "is_subscribed": str(user.is_subscribed),
        "subscription": {
            "id": user.subscription.id if user.subscription else "",
            "name": str(user.subscription.name) if user.subscription else "",
        },

        "role": {
            "id": user.role.id if user.role else "",
            "name": str(user.role) if user.role else ""
        },
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        ),
        "invited_by": user.property_id if user.property_id else None,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
