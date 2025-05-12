from djstripe.models import PaymentMethod
from stripe import Customer
from rest_framework import serializers
from payments.models import PaymentLogs

class PaymentMethodSerializer(serializers.ModelSerializer):
    is_default = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField()

    class Meta:
        model = PaymentMethod
        fields = '__all__'

    def get_is_default(self, obj):
        """Determine if this is the customer's default payment method."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                customer_id = request.user.stripe_customer_id
                stripe_customer = Customer.retrieve(str(customer_id))
                default_pm_stripe_id = stripe_customer.get('invoice_settings', {}).get('default_payment_method')
                if default_pm_stripe_id and str(obj.id) == str(default_pm_stripe_id):
                    return True

                return False
            except Exception as e:
                print(f"Error checking default payment method: {str(e)}")
                return False
        return False

    def get_card(self, obj):
        if obj.type == 'card' and isinstance(obj.card, dict):
            cd = obj.card
            checks = cd.get('checks', {})

            return {
                'brand': cd.get('brand'),
                'last4': cd.get('last4'),
                'exp_month': cd.get('exp_month'),
                'exp_year': cd.get('exp_year'),
                'checks': {
                    'cvc_check': checks.get('cvc_check'),
                    'address_line1_check': checks.get('address_line1_check'),
                    'address_postal_code_check': checks.get('address_postal_code_check'),
                },
                'country': cd.get('country'),
                'funding': cd.get('funding'),
                'fingerprint': cd.get('fingerprint'),
                'display_brand': cd.get('display_brand'),
                'regulated_status': cd.get('regulated_status'),
                'three_d_secure_usage': {
                    'supported': cd.get('three_d_secure_usage', {}).get('supported')
                }
            }
        return None


class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLogs
        fields = ['id', 'amount', 'details', 'is_deleted']