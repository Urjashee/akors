from jose import jwt, JWTError
from django.conf import settings
from django.contrib.auth import get_user_model

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

        user_id = payload.get("sub")
        return User.objects.filter(id=user_id).first()

    except JWTError:
        return None
