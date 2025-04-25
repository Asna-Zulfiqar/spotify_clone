from djstripe.models import PaymentMethod
from rest_framework import serializers
from payments.models import PaymentLogs


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class PaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLogs
        fields = ['id', 'amount', 'details', 'is_deleted']