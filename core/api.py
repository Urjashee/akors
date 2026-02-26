from ninja import NinjaAPI
from accounts.api import router as accounts_router
from stripe_integration.api import router as stripe_router
from ninja.security import HttpBearer
from accounts.auth import get_user_from_token

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        user = get_user_from_token(token)

        if not user:
            return None

        request.user = user
        return user

api = NinjaAPI(
    title="Todo API",
    version="1.0.0",
    auth=AuthBearer(),
)

api.add_router("/accounts/", accounts_router)
api.add_router("/stripe/", stripe_router)
