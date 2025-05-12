from rest_framework import serializers
from playlists.models import Playlist
from music.serializers import  SongResponseSerializer
from users.serializers import UserSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Playlist
        fields = ['id' ,'user', 'name' , 'privacy', 'total_songs', 'cover_image', 'created_at']

class PlaylistDetailSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id' , 'name' , 'cover_image', 'privacy', 'created_at', 'total_songs', 'songs', 'user']

    def get_songs(self, obj):
        return SongResponseSerializer(obj.songs.all(), many=True).data

    def get_user(self, obj):
        return UserSerializer(obj.user).data