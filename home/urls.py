from django.urls import path
from home.views import SearchAPI, RecommendationAPI

urlpatterns = [
    path('search/', SearchAPI.as_view(), name='search'),
    path('recommendations/', RecommendationAPI.as_view(), name='recommendations')
]