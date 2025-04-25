import stripe
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
    if not price_id:
        return Response({"error": "Invalid subscription type."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch  all subscriptions
        subscriptions = list(stripe.Subscription.list(
            customer=customer_id,
            status='all',
            expand=["data.default_payment_method"]
        ).auto_paging_iter())

        active_sub = None

        # Check for Active Subscriptions
        for sub in subscriptions:
            if sub.status in ['active'] and not sub.cancel_at_period_end:
                active_sub = sub

        # Check for Canceling Subscriptions that should be Reactivated
        for sub in subscriptions:
            if sub.status in ['active', 'trialing'] and sub.cancel_at_period_end:
                current_price = sub['items']['data'][0]['price']['id']
                if current_price == price_id:
                    stripe.Subscription.modify(sub.id, cancel_at_period_end=False)
                    return Response({"detail": "Subscription reactivated."}, status=status.HTTP_200_OK)
                else:
                    # Schedule New Plan after Current One ends and Cancels any other Scheduled Subscriptions
                    trial_end = sub['current_period_end']
                    existing_schedules = stripe.SubscriptionSchedule.list(customer=customer_id)
                    for schedule in existing_schedules.auto_paging_iter():
                        if schedule.status in ["not_started", "active"]:
                            stripe.SubscriptionSchedule.cancel(schedule.id)
                    schedule_sub = stripe.SubscriptionSchedule.create(
                        customer=customer_id,
                        start_date=trial_end,
                        end_behavior="release",
                        phases=[{
                            "items": [{"price": price_id}],
                            "default_payment_method": payment_method_id,
                        }]
                    )
                    return Response({
                        'detail': 'New subscription scheduled after current one ends.',
                        'schedule_id': schedule_sub.id
                    }, status=status.HTTP_201_CREATED)

        # Already Subscribed to this Exact Plan Or Have an Active Subscription
        if active_sub:
            current_price = active_sub['items']['data'][0]['price']['id']
            if current_price == price_id:
                return Response({"detail": "You are already subscribed to this plan."}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "detail": "You already have an active subscription. Please cancel it first to change your plan."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Create a new subscription
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            default_payment_method=payment_method_id,
            expand=["latest_invoice.payment_intent"]
        )

        # Log payment
        amount_cents = subscription['items']['data'][0]['price']['unit_amount']
        PaymentLogs.objects.create(
            user=user,
            amount=amount_cents / 100,
            details=f'Subscription to {subscription_type.capitalize()} Plan'
        )

        return Response({
            'detail': 'Subscription successful',
            'subscription_id': subscription.id
        }, status=status.HTTP_201_CREATED)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "An unexpected error occurred: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def unsubscribe(subscription_id):
    try:
        if subscription_id.startswith("sub_sched_"):
            stripe.SubscriptionSchedule.cancel(subscription_id)
            return Response({"detail": "Scheduled subscription has been canceled."},
                            status=status.HTTP_200_OK)
        else:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
                )
            return Response({"detail": "Subscription will be canceled at the end of the billing period."},
                                status=status.HTTP_200_OK)

    except stripe.error.InvalidRequestError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def list_my_subscriptions(customer_id):
    try:
        subscription_data = {
            "active_subscriptions": [],
            "scheduled_subscriptions": []
        }

        # Active subscriptions
        active = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            expand=["data.items.data.price"]
        )
        for sub in active['data']:
            subscription_data["active_subscriptions"].append(sub)

        # Scheduled subscriptions
        schedules = stripe.SubscriptionSchedule.list(customer=customer_id)
        for sched in schedules['data']:
            if sched['status'] in ('active', 'not_started'):
                subscription_data["scheduled_subscriptions"].append(sched)

        if not subscription_data["active_subscriptions"] and not subscription_data["scheduled_subscriptions"]:
            return Response({"detail": "No Active or Scheduled subscriptions found."},
                            status=status.HTTP_200_OK)

        return Response(subscription_data, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": f"Unexpected error: {e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)