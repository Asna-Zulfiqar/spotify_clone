from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import GoogleLoginAPIView
from users.viewsets import UserViewSet, ArtistRequestViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'artist-request', ArtistRequestViewSet, basename="artist-request")

urlpatterns = [
    path('', include(router.urls)),
    path('social/google/', GoogleLoginAPIView.as_view(), name='google-login'),
]
