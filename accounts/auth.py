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

        return User.objects.filter(id=int(user_id)).first()

    except ExpiredSignatureError:
        raise HttpError(401, "Token expired!")

    except JWTError:
        raise HttpError(401, "Invalid token!")
