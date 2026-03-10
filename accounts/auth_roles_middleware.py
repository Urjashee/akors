from ninja.errors import HttpError
from ninja.security import HttpBearer
from accounts.auth import get_user_from_token

class SuperAdminAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)
        print(user.role.name)
        if not user:
            raise HttpError(401, "Not a valid user!")

        if user.role.name != "Super admin":
            raise HttpError(403, "Not an admin user!")

        request.user = user
        return user

class PropertyManagerAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)
        print(user.role.name)
        if not user:
            if not user:
                raise HttpError(401, "Not a valid user!")

            if user.role.name != "Super admin":
                raise HttpError(403, "Not a propert manager user!")

        request.user = user
        return user