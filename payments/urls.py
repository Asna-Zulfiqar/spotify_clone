from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.viewsets import PaymentViewSet, PaymentLogListView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(router.urls)),
    path('payment_logs/', PaymentLogListView.as_view(), name='payment_logs')
]
