from django.urls import path, include
from rest_framework.routers import DefaultRouter
from music.viewsets import SongViewSet, AlbumViewSet

router = DefaultRouter()
router.register(r'songs', SongViewSet)
router.register(r'albums', AlbumViewSet)

urlpatterns = [
    path('', include(router.urls)),
]