from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from home.models import RecentlyPlayed
from home.utils import search, explore_page_recommendations
from music.serializers import SongSerializer
from playlists.serializers import PlaylistSerializer


class RecentlyPlayedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recently_played = {}
        recent = RecentlyPlayed.objects.filter(user=request.user).order_by('-played_at')
        recent_songs = [entry.song for entry in recent if entry.song]
        recent_playlists = [entry.playlist for entry in recent if entry.playlist]

        if recent_songs:
            recently_played['recently_played_songs'] = {
                'items': SongSerializer(recent_songs, many=True).data
            }

        if recent_playlists:
            recently_played['recently_played_playlists'] = {
                'items': PlaylistSerializer(recent_playlists, many=True).data
            }

        return Response(recently_played)

class SearchAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('query', None)
        type = request.query_params.get('type', None)

        if not query:
            return Response(
                {"error": "Search query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return search(query, type)

class ExplorePageAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return explore_page_recommendations(user)
