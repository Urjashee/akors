from ninja import NinjaAPI
from accounts.api import router as accounts_router

api = NinjaAPI(
    title="Akors API",
    version="1.0.0",
)

api.add_router("/accounts/", accounts_router)
