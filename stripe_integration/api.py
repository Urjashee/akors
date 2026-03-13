from ninja import Router
from django.db import transaction

from accounts.models import User
from accounts.auth_roles_middleware import PropertyManagerAuth, SuperAdminAuth
from stripe_integration.schemas import CreateCustomerSchema, ErrorSchema, SuccessSchema, CreateSubscriptionSchema, \
    UpdateSubscriptionSchema, UpdatePaymentMethod
from stripe_integration.services import create_customer, create_subscription, cancel_subscription, \
    get_subscription_details, get_upcoming_invoice, update_default_card, get_payment_method, get_all_invoice

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
                "data": None
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
                "data": None
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.get(
    "/subscription/details",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def subscription_details_api(request):
    try:
        user = User.objects.filter(email=request.user.email).first()

        if not user.stripe_subscription_id:
            return 400, {"status": "ERROR", "message": "No subscription found"}

        subscription = get_subscription_details(user.stripe_subscription_id)
        payment_method = get_payment_method(subscription.default_payment_method)
        invoices = get_all_invoice(user.customer_id)
        history = []

        for invoice in invoices.data:
            history.append({
                "invoice_id": invoice.id,
                "invoice_number": invoice.number,
                "amount_paid": invoice.amount_paid / 100,
                "currency": invoice.currency,
                "status": invoice.status,
                "invoice_date": invoice.created,
                "invoice_pdf": invoice.invoice_pdf
            })

        item = subscription["items"]["data"][0]

        data = {
            "subscription_id": subscription["id"],
            "status": subscription["status"],
            "plan_price": subscription["plan"]["amount"] / 100,
            "billing_interval": subscription["plan"]["interval"],
            "last_bill_amount": subscription["latest_invoice"]["amount_paid"] / 100,
            "last_bill_date": subscription["latest_invoice"]["status_transitions"]["paid_at"],
            "next_bill_date": item["current_period_end"],
            "cancelled": subscription["canceled_at"] is not None,
            "invoices": history,
            "default_payment_method": payment_method.card,
        }

        return 200, {
            "status": "SUCCESS",
            "message": "Subscription details retrieved successfully",
            "data": data
        }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}


@router.get(
    "/payment-method/update",
    response={200: SuccessSchema, 400: ErrorSchema},
)
def subscription_details_api(request, payload: UpdatePaymentMethod):
    try:
        with transaction.atomic():
            user = User.objects.filter(email=request.user.email).first()
            if not user.stripe_subscription_id:
                return 400, {"status": "ERROR", "message": "No subscription found"}

            update_card = update_default_card(user.customer_id, user.stripe_subscription_id, payload.amount)
            if not update_card:
                return 400, {"status": "ERROR", "message": "Could not update default card"}

            return 200, {
                "status": "SUCCESS",
                "message": "Payment method updated successfully",
                "data": None
            }

    except Exception as e:
        return 400, {"status": "ERROR", "message": str(e)}