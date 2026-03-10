from ninja import NinjaAPI
from ninja.errors import HttpError

from accounts.api import router as accounts_router
from accounts.config import router as config_router
from stripe_integration.api import router as stripe_router
from property.api import router as property_router
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
api.add_router("/config/", config_router)
api.add_router("/stripe/", stripe_router)
api.add_router("/property/", property_router)

@api.exception_handler(HttpError)
def http_error_handler(request, exc):
    status = "ERROR"
    if exc.status_code == 403:
        status = "FORBIDDEN"

    if exc.status_code == 401:
        status = "UNAUTHORIZED"

    return api.create_response(
        request,
        {
            "status": status,
            "message": str(exc.message),
        },
        status=exc.status_code,
    )
