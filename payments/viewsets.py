import stripe
from django.conf import settings
from djstripe.models import PaymentMethod
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from payments.models import PaymentLogs
from payments.serializers import PaymentMethodSerializer, PaymentLogSerializer
from payments.utils import add_stripe_account, add_payment_method, get_stripe_account, subscribe, unsubscribe, \
    list_my_subscriptions

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class PaymentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PaymentMethod.objects.none()

    @action(detail=False, methods=['post'])
    def add_stripe_account(self, request):
        user = request.user
        return add_stripe_account(user)

    @action(detail=False, methods=['get'])
    def view_stripe_account(self, request):
        return get_stripe_account(request.user)

    @action(detail=False, methods=["post"])
    def add_payment_method(self, request):
        user = request.user
        payment_method_id = request.data.get("payment_method_id")

        if not payment_method_id:
            return Response({"error": "Payment method ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        return add_payment_method(user, payment_method_id)

    @action(detail=False, methods=["get"])
    def list_payment_methods(self, request):
        customer = request.user.stripe_customer_id
        methods = PaymentMethod.objects.filter(customer=customer)
        serializer = PaymentMethodSerializer(methods, many=True, context={"request": request})
        return Response({"methods": serializer.data})

    @action(detail=False, methods=['post'])
    def set_default_payment_method(self, request):
        payment_method_id = request.data.get("payment_method_id")
        customer_id = request.user.stripe_customer_id

        try:
            pm = PaymentMethod.objects.get(id=payment_method_id, customer=customer_id)
            customer_id_str = str(customer_id)
            payment_method_id_str = str(pm.id)
            stripe.Customer.modify(
                customer_id_str,
                invoice_settings={
                    'default_payment_method': payment_method_id_str
                }
            )
            return Response({'status': 'Default payment method updated'})
        except PaymentMethod.DoesNotExist:
            return Response({'error': 'Payment method not found'}, status=404)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Error setting default payment method: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=500)

    @action(detail=False, methods=['post'])
    def revoke_payment_method(self, request):
        payment_method_id = request.data.get("payment_method_id")
        customer = request.user.stripe_customer_id
        try:
            pm = PaymentMethod.objects.get(id=payment_method_id, customer=customer)
            pm.detach()
            return Response({'status': 'Payment method revoked'})
        except PaymentMethod.DoesNotExist:
            return Response({'error': 'Payment method not found'}, status=404)


    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        user = request.user
        subscription_type = request.data.get("subscription_type")
        payment_method_id = request.data.get("payment_method_id")

        if not subscription_type or subscription_type not in settings.STRIPE_PRICE_IDS:
            return Response({"error": "Valid subscription type is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not payment_method_id:
            return Response({"error": "Payment method ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        response = subscribe(user, subscription_type, payment_method_id)
        return response

    @action(detail=False, methods=['post'])
    def cancel_subscription(self, request):
        subscription_id = request.data.get("subscription_id")
        if not subscription_id:
            return Response({"error": "Subscription ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        response = unsubscribe(subscription_id)
        return response

    @action(detail=False, methods=['get'])
    def list_my_subscriptions(self, request):
        user = request.user
        customer_id = user.stripe_customer_id

        if not customer_id:
            return Response({"error": "User does not have a Stripe account."}, status=status.HTTP_400_BAD_REQUEST)

        response = list_my_subscriptions(customer_id)
        return response


class PaymentLogListView(ListAPIView):
    serializer_class = PaymentLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentLogs.objects.filter(
            user=self.request.user,
            is_deleted=False
        )