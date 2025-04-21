from django.urls import path, include
from rest_framework.routers import DefaultRouter
from music.views import LikeSongView, UnlikeSongView, FollowUserView, UnFollowUserView
from music.viewsets import SongViewSet, AlbumViewSet

router = DefaultRouter()
router.register(r'songs', SongViewSet)
router.register(r'albums', AlbumViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('like-song/', LikeSongView.as_view(), name='like-song'),
    path('unlike-song/', UnlikeSongView.as_view(), name='unlike-song'),
    path('follow_user/', FollowUserView.as_view(), name='follow_user'),
    path('unfollow_user/', UnFollowUserView.as_view(), name='unfollow_user')
]