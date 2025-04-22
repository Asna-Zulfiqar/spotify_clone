from django.urls import path
from home.views import SearchAPI, ExplorePageAPI, RecentlyPlayedAPIView

urlpatterns = [
    path('recently_played/', RecentlyPlayedAPIView.as_view(), name='recently_played'),
    path('search/', SearchAPI.as_view(), name='search'),
    path('explore/', ExplorePageAPI.as_view(), name='recommendations')
]