from django.contrib.auth import get_user_model
from rest_framework import serializers
from music.models import Album, Genre, Song
from users.serializers import UserSerializer

User = get_user_model()

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class SongSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    featured_artists = serializers.ListField(child=serializers.UUIDField(), required=False, write_only=True)

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'song_cover_image', 'album', 'featured_artists', 'duration', 'category', 'lyrics', 'genres', 'audio_file',
            'plays_count', 'description','created_at', 'released_date']
        extra_kwargs = {
            'album': {'required': False}
        }

    def create(self, validated_data):
        genre_names = validated_data.pop('genres', [])
        featured_artist_ids = validated_data.pop('featured_artists', [])
        album = validated_data.get('album')

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
        genre_names = validated_data.pop('genres', [])
        album = Album.objects.create(**validated_data)

        if genre_names:
            genres = []
            for genre_name in genre_names:
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                genres.append(genre)

            album.genres.set(genres)

        return album

    def update(self, instance, validated_data):
        genre_names = validated_data.pop('genres', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for genre_name in genre_names:
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            instance.genres.add(genre)

        return instance


class AlbumResponseSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'description', 'release_date', 'cover_image', 'total_songs', 'genres', 'songs']

class SongResponseSerializer(serializers.ModelSerializer):
    genre_details = GenreSerializer(many=True, read_only=True, source='genre')
    featured_artists_details = UserSerializer(many=True, read_only=True)
    album_details = AlbumSerializer(source='album', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id', 'title', 'song_cover_image', 'album', 'album_details', 'featured_artists_details', 'duration', 'category', 'lyrics', 'genre_details',
            'audio_file', 'plays_count', 'description', 'created_at', 'released_date']