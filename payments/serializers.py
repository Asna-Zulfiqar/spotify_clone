from djstripe.models import PaymentMethod
from rest_framework import serializers


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"