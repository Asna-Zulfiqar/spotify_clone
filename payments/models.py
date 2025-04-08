from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PaymentLogs(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_logs')
    amount = models.FloatField(null=True)
    details = models.CharField(max_length=100, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f" {self.user.username} Payment Log"
