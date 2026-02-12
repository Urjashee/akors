from datetime import datetime, timedelta
from jose import jwt
from django.conf import settings

def create_access_token(user: any):
    payload = {
        "id": str(user.id),
        "email": str(user.email),
        "first_name": str(user.first_name),
        "last_name": str(user.last_name),
        "is_subscribed": str(user.is_subscribed),
        "subscription_id": str(user.subscription),
        "type": "access",
        "exp": datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user: any):
    payload = {
        "id": str(user.id),
        "email": str(user.email),
        "first_name": str(user.first_name),
        "last_name": str(user.last_name),
        "is_subscribed": str(user.is_subscribed),
        "subscription_id": str(user.subscription),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        ),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
