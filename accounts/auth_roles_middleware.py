from ninja.errors import HttpError
from ninja.security import HttpBearer
from accounts.auth import get_user_from_token

class SuperAdminAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)

        if not user:
            raise HttpError(401, "Not a valid user!")

        if user.role.name != "Super admin":
            raise HttpError(403, "Not an admin user!")

        request.user = user
        return user

class PropertyManagerAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)

        if not user:
            raise HttpError(401, "Not a valid user!")

        print(user.role.name)

        if user.role.name != "Property manager":
            raise HttpError(403, "Not a property manager user!")

        request.user = user
        return user


class OperatorAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)

        if not user:
            raise HttpError(401, "Not a valid user!")

        if user.role.name != "Operator":
            raise HttpError(403, "Not an admin user!")

        request.user = user
        return user