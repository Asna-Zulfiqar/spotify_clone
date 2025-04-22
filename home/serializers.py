from rest_framework import serializers
from home.models import RecentlyPlayed
from music.serializers import SongSerializer
from playlists.serializers import PlaylistSerializer


class RecentlyPlayedSerializer(serializers.ModelSerializer):
    song = SongSerializer()
    playlist = PlaylistSerializer()

    class Meta:
        model = RecentlyPlayed
        fields = ['song', 'playlist', 'played_at']