import secrets
from datetime import timedelta

from django.utils import timezone
from ninja import Router
from django.db import transaction
from django.db.models import F

from ninja import Query

from accounts.models import User
from stripe_integration.schemas import CreateCustomerSchema, ErrorSchema, SuccessSchema, CreateSubscriptionSchema
from stripe_integration.services import create_customer, create_subscription

router = Router(tags=["stripe"])


# STEP 4 — Create Customer (Backend)
@router.post(
    "/customers/create",
    auth=None,
    response={
        200: SuccessSchema,
        400: ErrorSchema,
    },
)
def create_customer_view(request, payload: CreateCustomerSchema):
    try:
        with transaction.atomic():

            customer_data = create_customer(
                payload.email,
                payload.name
            )

            if not customer_data:
                return 400, {
                    "status": "ERROR",
                    "message": "Could not create customer.",
                }

            return 200, {
                "status": "SUCCESS",
                "message": "Customer created successfully.",
                "data": customer_data,
            }

    except Exception as e:
        return 400, {
            "status": "ERROR",
            "message": str(e),
        }


# STEP 5.1 — First-Time Payment Method Setup (IMPORTANT)

# STEP 5.2 — Attach Payment method

# STEP 6 — Set Default Payment Method (Backend)

# STEP 7 — Create Subscription (Fully Backend Controlled)
@router.post(
    "/subscription/create",
    # auth=None,
    response={200: SuccessSchema, 400: ErrorSchema},
)
def create_subscription_api(request, payload: CreateSubscriptionSchema):
    try:
        with transaction.atomic():

            user = User.objects.filter(email=request.user.email).first()

            if user.customer_id is None:
                customer = create_customer(user.email, user.first_name)

                if not customer:
                    return 400, {"status": "ERROR", "message": "Could not create customer"}

                user.customer_id = customer["id"]
                user.save()

            subscription = create_subscription(
                user.customer_id,
                payload.price_id
            )

            if not subscription:
                return 400, {"status": "ERROR", "message": "Could not create subscription"}

            user.stripe_subscription_id = subscription["subscription_id"]
            user.subscription_id = payload.subscription_type_id
            user.is_subscribed = True
            user.save()

            return 200, {
                "status": "SUCCESS",
                "message": "Subscription created successfully",
                "data": subscription,
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}
