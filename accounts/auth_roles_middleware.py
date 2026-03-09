from ninja.security import HttpBearer
from accounts.auth import get_user_from_token

class SuperAdminAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)
        # print(user.role.name)
        if not user:
            return None

        if user.role.name != "Super admin":
            return None

        request.user = user
        return user

class PropertyManagerAuth(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)

        if not user:
            return None

        if user.role.name != "Property manager":
            return None

        request.user = user
        return user