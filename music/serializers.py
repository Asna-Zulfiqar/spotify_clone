from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from music.models import Album, Genre, Song, LikeSong, UnlikeSong

User = get_user_model()

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class SongSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    featured_artists = serializers.ListField(child=serializers.UUIDField(), required=False, write_only=True)
    featured_artists_details = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'song_cover_image', 'album', 'featured_artists', 'featured_artists_details', 'duration',
            'lyrics', 'genres', 'audio_file', 'plays_count', 'description','created_at', 'released_date']
        extra_kwargs = {
            'album': {'required': False}
        }

    def create(self, validated_data):
        genre_names = validated_data.pop('genres', [])
        featured_artist_ids = validated_data.pop('featured_artists', [])
        album = validated_data.get('album')

        with transaction.atomic():
            song = Song.objects.create(**validated_data)

            if genre_names:
                genres = []
                for genre_name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    genres.append(genre)

                song.genre.set(genres)

            if featured_artist_ids:
                featured_artists = []
                for artist in featured_artist_ids:
                    try:
                        artist = User.objects.get(id=artist)
                        featured_artists.append(artist)
                    except User.DoesNotExist:
                        song.delete()
                        raise serializers.ValidationError(
                            f"Artist with UUID '{artist}' does not exist"
                        )

                song.featured_artists.set(featured_artists)

            if album:
                try:
                    album_instance = Album.objects.get(id=album.id)
                    album_instance.total_songs += 1
                    album_instance.save()
                except Album.DoesNotExist:
                    song.delete()
                    raise serializers.ValidationError("Album not found")
        return song

    def update(self, instance, validated_data):
        genre_names = validated_data.pop('genres', [])
        featured_artist_ids = validated_data.pop('featured_artists', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if genre_names:
            for genre_name in genre_names:
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                instance.genre.add(genre)

        if featured_artist_ids:
            for artist in featured_artist_ids:
                try:
                    artist = User.objects.get(id=artist)
                    instance.featured_artists.add(artist)
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"Artist with UUID '{artist}' does not exist")

        return instance

    def get_featured_artists_details(self, obj):
        from users.serializers import UserResponseSerializer
        return UserResponseSerializer(obj.featured_artists.all(), many=True).data


class AlbumSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)

    class Meta:
        model = Album
        fields = [
            'title', 'artist', 'description', 'release_date', 'cover_image', 'total_songs', 'genres']
        extra_kwargs = {
            'artist': {'required': False},
            'total_songs': {'required': False}
        }

    def create(self, validated_data):
        album = Album.objects.create(**validated_data)
        return album

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AlbumResponseSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
    artist = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'description', 'release_date', 'cover_image', 'total_songs', 'songs']

    def get_artist(self, obj):
        from users.serializers import UserResponseSerializer
        return UserResponseSerializer(obj.artist).data

class SongResponseSerializer(serializers.ModelSerializer):
    genre_details = GenreSerializer(many=True, read_only=True, source='genre')
    featured_artists_details = serializers.SerializerMethodField()
    album_details = AlbumResponseSerializer(source='album', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'song_cover_image', 'album', 'album_details', 'featured_artists_details', 'duration', 'likes', 'dislikes',
            'lyrics', 'genre_details', 'audio_file', 'plays_count', 'description', 'created_at', 'released_date']

    def get_featured_artists_details(self, obj):
        from users.serializers import UserResponseSerializer
        return UserResponseSerializer(obj.featured_artists.all(), many=True).data

class LikeSongSerializer(serializers.ModelSerializer):
    song = serializers.PrimaryKeyRelatedField( queryset=Song.objects.all(), required=True,
                                               error_messages={"does_not_exist": "Song not found with this id"})

    class Meta:
        model = LikeSong
        fields = ['song']

class LikeSongResponseSerializer(serializers.ModelSerializer):
    song = SongResponseSerializer()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = LikeSong
        fields = ['song', 'display_name']

    def get_display_name(self, obj):
        return obj.song.album.artist.user_profile.display_name


class UnlikeSongSerializer(serializers.ModelSerializer):
    song = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), required=True,
                                              error_messages={"does_not_exist": "Song not found with this id"})

    class Meta:
        model = UnlikeSong
        fields = ['song']


class FollowUserSerializer(serializers.ModelSerializer):
    followed = serializers.PrimaryKeyRelatedField( queryset=User.objects.all(), required=True,
                                                   error_messages={"does_not_exist": "User not found with this id"})

    class Meta:
        model = LikeSong
        fields = ['followed']