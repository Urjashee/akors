import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_customer(email, name=None):
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
        )

        return {
            "id": customer.id,
            "email": customer.email,
            "name": customer.name,
        }

    except stripe.StripeError as e:
        print("Stripe Error:", str(e))
        return None


def create_subscription(customer_id, price_id):
    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,  # cus_U37CoNohPEHeTC
            items=[{"price": price_id}],  # price_1T504UBDnPGPFOY8VTUSq0Wc
            payment_settings={
                "save_default_payment_method": "on_subscription"
            },
            collection_method="charge_automatically",
            expand=["latest_invoice.confirmation_secret"],
        )

        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.confirmation_secret.client_secret,
        }

    except stripe.StripeError as e:
        print("Stripe Error:", str(e))
        return None


def create_session(user, payload, settings):
    try:
        return stripe.checkout.Session.create(
            customer=user.customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": payload.price_id,
                    "quantity": 1,
                }
            ],
            success_url=f"{settings.FRONTEND_URL}/subscription-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/subscription-cancel",
            metadata={
                "user_id": user.id,
                "subscription_type_id": payload.subscription_type_id,
            }
        )

    except stripe.StripeError as e:
        print("Stripe Error:", str(e))
        return None


def update_web_hook(payload, sig_header):
    try:
        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.getenv("STRIPE_WEBHOOK_SECRET")
        )
    except stripe.StripeError as e:
        print("Stripe Error:", str(e))
        return None


def cancel_subscription(subscription_id):
    try:
        subscription = stripe.Subscription.delete(subscription_id)

        return {
            "subscription_id": subscription.id,
            "status_value": subscription.status
        }

    except stripe.StripeError as e:
        print("Stripe Error:", str(e))
        return None


def get_subscription_details(subscription_id):
    try:
        subscription = stripe.Subscription.retrieve(
            subscription_id,
            expand=["latest_invoice", "latest_invoice.payment_intent"]
        )

        return subscription

    except stripe.StripeError as e:
        print("Stripe Error:", str(e))
        return None


def get_upcoming_invoice(customer_id, subscription_id):
    try:
        upcoming_invoice = stripe.Invoice.upcoming(
            customer=customer_id,
            subscription=subscription_id
        )

        return upcoming_invoice

    except stripe.StripeError:
        return None


def get_all_invoice(customer_id):
    try:
        invoices = stripe.Invoice.list(
            customer=customer_id,
        )

        return invoices

    except stripe.StripeError:
        return None


def get_payment_method(customer_id):
    try:
        customer = stripe.Customer.retrieve(customer_id)
        payment_method_id = customer.invoice_settings.default_payment_method

        if not payment_method_id:
            return None

        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        # print("Method:", payment_method)
        return payment_method

    except stripe.StripeError:
        return None


def update_default_card(customer_id, subscription_id, payment_method_id):
    try:
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )

        stripe.Customer.modify(
            customer_id,
            invoice_settings={
                "default_payment_method": payment_method_id
            }
        )

        stripe.Subscription.modify(
            subscription_id,
            default_payment_method=payment_method_id
        )

        return True

    except stripe.error.StripeError as e:
        print(str(e))
        return False


def get_invoice_details(invoice):
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.number,
        "amount_paid": invoice.amount_paid / 100,
        "currency": invoice.currency,
        "status": invoice.status,
        "invoice_date": invoice.created,
        "invoice_pdf": invoice.invoice_pdf
    }


def get_sub_details(subscription, item, history, payment_method, active_subscription):
    return {
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
        "active_subscription": active_subscription
    }


def has_active_subscription(customer_id):
    subscriptions = stripe.Subscription.list(
        customer=customer_id,
        status="active",
        limit=1
    )

    return len(subscriptions.data) > 0
