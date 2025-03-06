from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.viewsets import UserViewSet, ArtistRequestViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'artist-request', ArtistRequestViewSet, basename="artist-request")

urlpatterns = [
    path('', include(router.urls)),
]
