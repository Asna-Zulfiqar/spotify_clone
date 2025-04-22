from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from home.utils import add_to_recently_played
from playlists.models import Playlist
from playlists.serializers import PlaylistSerializer, PlaylistDetailSerializer
from playlists.utils import add_or_remove_song_to_playlist


class PlaylistViewSet(ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Playlist.objects.filter(privacy='public')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = PlaylistSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        add_to_recently_played(user, playlist=instance)
        serializer = PlaylistDetailSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_playlists(self, request):
        playlists = Playlist.objects.filter(user=request.user)
        serializer = PlaylistSerializer(playlists, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_or_remove_song(self, request, *args, **kwargs):
        song_id = request.data.get('song_id')
        playlist_id = request.data.get('playlist_id')
        if not playlist_id or not song_id:
            return Response({'error': 'Missing playlist_id or song_id'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        return add_or_remove_song_to_playlist(user, playlist_id, song_id)


    @action(detail=False, methods=['delete'])
    def delete_playlist(self, request):
        playlist_id = request.data.get('playlist_id')
        if not playlist_id:
            return Response({'error': 'Missing playlist_id'}, status=status.HTTP_400_BAD_REQUEST)
        playlist = Playlist.objects.get(id=playlist_id)
        playlist.delete()
        return Response({'message': 'Playlist deleted successfully'}, status=status.HTTP_204_NO_CONTENT)





