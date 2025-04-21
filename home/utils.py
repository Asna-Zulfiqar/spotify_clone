from django.contrib.auth import get_user_model
from rest_framework.response import Response
from music.models import Song, Album, LikeSong, Follow
from music.serializers import SongSerializer, AlbumResponseSerializer, SongResponseSerializer, AlbumSerializer
from playlists.models import Playlist
from playlists.serializers import PlaylistSerializer
from users.serializers import ArtistSerializer
from django.contrib.postgres.search import SearchVector
from django.db.models import Q, Count

User = get_user_model()

def search(query, type):
    results = {}

    if not type or type == 'songs':
        songs = Song.objects.annotate(
            search=SearchVector('title', 'album__title', 'album__artist__user_profile__display_name')
        ).filter(search=query)
        results['songs'] = SongSerializer(songs, many=True).data

    if not type or type == 'albums':
        albums = Album.objects.annotate(
            search=SearchVector('title', 'artist__user_profile__display_name')
        ).filter(search=query)
        results['albums'] = AlbumResponseSerializer(albums, many=True).data

    if not type or type == 'artists':
        artists = User.objects.annotate(
            search=SearchVector('first_name', 'last_name', 'user_profile__display_name')
        ).filter(Q(user_profile__role='artists') & Q(search=query)).distinct()
        results['artists'] = ArtistSerializer(artists, many=True).data

    if not type or type == 'playlists':
        playlists = Playlist.objects.annotate(
            search=SearchVector('name', 'user__user_profile__display_name')
        ).filter(search=query, privacy='public')
        results['playlists'] = PlaylistSerializer(playlists, many=True).data

    return Response(results)

def user_recommendations(user):
    recommendations = {}

    liked_song_ids = LikeSong.objects.filter(user=user).values_list('song_id', flat=True)
    liked_genres = Song.objects.filter(id__in=liked_song_ids).values_list('genre', flat=True)

    if liked_song_ids.exists():
        genre_based_songs = Song.objects.filter(genre__in=liked_genres).exclude(id__in=liked_song_ids).distinct()
        recommendations['songs'] = SongSerializer(genre_based_songs, many=True).data


    return Response(recommendations)
