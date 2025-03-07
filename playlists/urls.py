from django.urls import path, include
from rest_framework.routers import DefaultRouter
from playlists.viewsets import PlaylistViewSet

router = DefaultRouter()

router.register('playlists', PlaylistViewSet)

urlpatterns = [
    path('' , include(router.urls))
]