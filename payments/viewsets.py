import stripe
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from payments.utils import add_stripe_account

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class PaymentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def add_stripe_account(self, request):
        user = request.user
        return add_stripe_account(user)
