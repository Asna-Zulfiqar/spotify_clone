from datetime import datetime

import stripe
from django.db import transaction
from djstripe.models import Account, Customer, PaymentMethod
from rest_framework import status
from rest_framework.response import Response

from payments.models import PaymentLogs
from spotify_clone.settings import STRIPE_PRICE_IDS

# Stripe URL
STRIPE_PROFILE_REFRESH_LINK = "http://localhost:8000/api/payments/refresh"
STRIPE_PROFILE_REDIRECT_LINK = "http://localhost:8000/api/payments/return"


def add_stripe_account(user):
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email)
        djstripe_customer = Customer.sync_from_stripe_data(customer)
        user.stripe_customer_id = djstripe_customer
        user.save()

    if user.stripe_account:
        account_id = user.stripe_account.id
        account = stripe.Account.retrieve(account_id)
        return Response({'message': "Already have a Stripe Account", 'details': account})

    else:
        account = stripe.Account.create(
            type="express",
            country="US",
            email=user.email,
            capabilities={
                "transfers": {"requested": True},
                "card_payments": {"requested": True}
            },
            business_type="individual",
            business_profile={"name": user.email}
        )

        djstripe_account = Account.sync_from_stripe_data(account)
        user.stripe_account = djstripe_account
        user.save()

    account_link = stripe.AccountLink.create(
        account=user.stripe_account.id,
        refresh_url=STRIPE_PROFILE_REFRESH_LINK,
        return_url=STRIPE_PROFILE_REDIRECT_LINK,
        type="account_onboarding"
    )

    return Response({'Stripe Link': account_link['url']})

def get_stripe_account(user):
    if user.stripe_account:
        account_id = user.stripe_account.id
        account = stripe.Account.retrieve(account_id)
        return Response(account)
    else:
        return Response({"detail": "Stripe details not added"}, status=status.HTTP_400_BAD_REQUEST)


def add_payment_method(user, payment_method_id):
    try:
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            djstripe_customer = Customer.sync_from_stripe_data(customer)
            user.stripe_customer_id = djstripe_customer
            user.save()
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id.id)

        PaymentMethod.attach(payment_method_id, customer=customer.id)
        stripe.Customer.modify(
            customer.id,
            invoice_settings={"default_payment_method": payment_method_id},
        )
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
            type="card"
        ).data
        return Response(payment_methods, status=status.HTTP_201_CREATED)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def subscribe(user, subscription_type, payment_method_id):
    customer_id = user.stripe_customer_id
    if not customer_id:
        return Response(
            {"details": "User does not have a Stripe account. Kindly create one before subscribing."},
            status=status.HTTP_400_BAD_REQUEST
        )


    price_id = STRIPE_PRICE_IDS.get(subscription_type)

    try:
        with transaction.atomic():
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                expand=["latest_invoice.payment_intent"]
            )

            amount_cents = subscription['items']['data'][0]['price']['unit_amount']
            amount_dollars = amount_cents / 100

            PaymentLogs.objects.create(
                user=user,
                amount=amount_dollars,
                details=f'Subscription to {subscription_type.capitalize()} Plan'
            )

        return Response({'detail': 'Subscription successful'}, status=status.HTTP_201_CREATED)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def unsubscribe(user, subscription_id):
    try:
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return Response({"detail": "Subscription will be canceled at the end of the billing period."},
                        status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def list_my_subscriptions(customer_id):
    try:
        subscriptions = stripe.Subscription.list(customer=customer_id)
        subscription_data = []

        if not subscriptions:
            return Response({"detail": "No subscriptions found."}, status=status.HTTP_400_BAD_REQUEST)

        for sub in subscriptions['data']:
            subscription_data.append({
                "id": sub["id"],
                "status": sub["status"],
                "current_period_start": datetime.utcfromtimestamp(sub["current_period_start"]).strftime('%Y-%m-%d'),
                "cancel_at_period_end": sub["cancel_at_period_end"],
                "items": [
                    {
                        "price_id": item["price"]["id"],
                        "amount": item["price"]["unit_amount"] / 100,
                        "currency": item["price"]["currency"]
                    }
                    for item in sub["items"]["data"]
                ]
            })

        return Response({"subscriptions": subscription_data}, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": "An unexpected error occurred: " + str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)