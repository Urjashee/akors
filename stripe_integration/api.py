from ninja import Router
from django.db import transaction

from accounts.models import User
from accounts.auth_roles_middleware import PropertyManagerAuth, SuperAdminAuth
from stripe_integration.schemas import CreateCustomerSchema, ErrorSchema, SuccessSchema, CreateSubscriptionSchema, \
    UpdateSubscriptionSchema
from stripe_integration.services import create_customer, create_subscription, cancel_subscription

router = Router(tags=["stripe"])


# Create Customer (Backend)
@router.post(
    "/customers/create",
    auth=None,
    response={200: SuccessSchema, 400: ErrorSchema},
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


# Create Subscription (Fully Backend Controlled)
@router.post(
    "/subscription/create",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def create_subscription_api(request, payload: CreateSubscriptionSchema):
    try:
        with transaction.atomic():
            print(request.user.email)
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

            # user.stripe_subscription_id = subscription["subscription_id"]
            # user.subscription_id = payload.subscription_type_id
            # user.is_subscribed = True
            # user.save()

            return 200, {
                "status": "SUCCESS",
                "message": "Subscription created successfully",
                "data": {
                    "stripe_subscription_id": subscription["subscription_id"],
                    "client_secret": subscription["client_secret"],
                    "subscription_id": payload.subscription_type_id,
                    "user_id": user.id,
                }
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


# Update subscription details from url
@router.post(
    "/subscription/update",
    auth=None,
    response={200: SuccessSchema, 400: ErrorSchema},
)
def update_subscription(request, payload: UpdateSubscriptionSchema):
    try:
        with transaction.atomic():
            user = User.objects.filter(id=request.payload.user_id).first()

            if user.stripe_subscription_id:
                delete_subscription = cancel_subscription(user.stripe_subscription_id)
                if not delete_subscription:
                    return 400, {"status": "ERROR", "message": "Could not delete previous subscription"}

            user.stripe_subscription_id = payload.stripe_subscription_id
            user.subscription_id = payload.subscription_type_id
            user.is_subscribed = True
            user.save()

            return 200, {
                "status": "SUCCESS",
                "message": "Subscription updated successfully",
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


# Update subscription details from url
@router.post(
    "/subscription/cancel",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def cancel_subscription(request):
    try:
        with transaction.atomic():
            user = User.objects.filter(email=request.user.email).first()

            if user.stripe_subscription_id:
                delete_subscription = cancel_subscription(user.stripe_subscription_id)
                if not delete_subscription:
                    return 400, {"status": "ERROR", "message": "Could not delete subscription"}

            user.stripe_subscription_id = None
            user.is_subscribed = False
            user.save()

            return 200, {
                "status": "SUCCESS",
                "message": "Subscription deleted successfully",
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}
