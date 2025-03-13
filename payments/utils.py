import stripe
from djstripe.models import Account, Customer
from rest_framework.response import Response

# Stripe URL
STRIPE_PROFILE_REFRESH_LINK = "http://localhost:8000/api/payments/refresh"
STRIPE_PROFILE_REDIRECT_LINK = "http://localhost:8000/api/payments/return"


def add_stripe_account(user):
    # Create Stripe customer if not exists
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email)
        djstripe_customer = Customer.sync_from_stripe_data(customer)
        user.stripe_customer_id = djstripe_customer  # Store as object reference
        user.save()

    # Check if user already has a Stripe account
    if user.stripe_account:
        account_id = user.stripe_account.id  # Use the referenced object's ID
        account = stripe.Account.retrieve(account_id)
        return Response({'message': "Already have a Stripe Account", 'details': account})

    else:
        # Create a new Stripe Express account
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

        # Sync the account with dj-stripe
        djstripe_account = Account.sync_from_stripe_data(account)
        user.stripe_account = djstripe_account  # Store as object reference
        user.save()

    # Generate onboarding link
    account_link = stripe.AccountLink.create(
        account=user.stripe_account.id,  # Use stored account ID
        refresh_url=STRIPE_PROFILE_REFRESH_LINK,
        return_url=STRIPE_PROFILE_REDIRECT_LINK,
        type="account_onboarding"
    )

    return Response({'Stripe Link': account_link['url']})
