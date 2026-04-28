from jose import jwt, JWTError, ExpiredSignatureError
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.errors import HttpError

User = get_user_model()

def get_user_from_token(token: str):
    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            return None

        user_id = payload.get("id")

        user = User.objects.filter(id=int(user_id)).first()

        if user and not user.is_active:
            raise HttpError(401, "Account has been deactivated.")

        return user

    except ExpiredSignatureError:
        raise HttpError(401, "Token expired!")

    except JWTError:
        raise HttpError(401, "Invalid token!")


def get_user_from_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HttpError(401, "Invalid refresh token")

        user_id = payload.get("id")

        user = User.objects.filter(id=user_id).first()

        if not user:
            raise HttpError(401, "User not found")

        return user, payload

    except ExpiredSignatureError:
        raise HttpError(401, "Refresh token expired!")

    except JWTError:
        raise HttpError(401, "Invalid refresh token!")
