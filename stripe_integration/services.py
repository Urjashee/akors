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
            customer=customer_id, #cus_U37CoNohPEHeTC
            items=[{"price": price_id}], # price_1T504UBDnPGPFOY8VTUSq0Wc
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