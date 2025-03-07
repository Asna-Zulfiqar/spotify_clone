from rest_framework import serializers
from playlists.models import Playlist
from music.serializers import  SongResponseSerializer
from users.serializers import UserSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id' , 'name' , 'privacy', 'total_songs']

class PlaylistDetailSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id' , 'name' , 'privacy', 'total_songs', 'songs', 'user']

    def get_songs(self, obj):
        return SongResponseSerializer(obj.songs.all(), many=True).data

    def get_user(self, obj):
        return UserSerializer(obj.user).data