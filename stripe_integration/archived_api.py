from django.conf import settings
from ninja import Router
from django.db import transaction

from accounts.models import User
from accounts.auth_roles_middleware import PropertyManagerAuth, SuperAdminAuth
from stripe_integration.schemas import CreateCustomerSchema, ErrorSchema, SuccessSchema, CreateSubscriptionSchema, \
    UpdateSubscriptionSchema, UpdatePaymentMethod
from stripe_integration.services import create_customer, create_subscription, cancel_subscription, \
    get_subscription_details, get_upcoming_invoice, update_default_card, get_payment_method, get_all_invoice, \
    create_session, update_web_hook

router = Router(tags=["stripe-archived"])
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
                "data": None
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}