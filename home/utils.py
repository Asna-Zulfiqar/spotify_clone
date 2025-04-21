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

    # -------------------- 1. Liked Songs --------------------
    liked_song_ids = LikeSong.objects.filter(user=user).values_list('song_id', flat=True)
    liked_genres = Song.objects.filter(id__in=liked_song_ids).values_list('genre', flat=True)

    if liked_song_ids.exists():
        genre_based_songs = Song.objects.filter(genre__in=liked_genres).exclude(id__in=liked_song_ids).distinct()[:10]
        recommendations['songs'] = SongSerializer(genre_based_songs, many=True).data

    # -------------------- 2. Followed Artists --------------------
    followed_artist_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)

    if followed_artist_ids.exists():
        artist_songs = Song.objects.filter(
            Q(album__artist__id__in=followed_artist_ids) | Q(featured_artists__id__in=followed_artist_ids)
        ).distinct()[:10]
        recommendations['artist_songs'] = SongSerializer(artist_songs, many=True).data

        artist_albums = Album.objects.filter(artist__id__in=followed_artist_ids)[:5]
        recommendations['artist_albums'] = AlbumSerializer(artist_albums, many=True).data

    # -------------------- 3. Songs in User’s Playlist --------------------
    elif user.user_playlist.exists():
        playlist_songs = Song.objects.filter(playlists__user=user).values_list('id', flat=True)
        popular_outside = Song.objects.exclude(id__in=playlist_songs).order_by('-plays_count')[:10]
        recommendations['songs'] = SongSerializer(popular_outside, many=True).data

    # -------------------- 4. Fallback: Trending Songs --------------------
    if 'songs' not in recommendations:
        trending_songs = Song.objects.order_by('-plays_count')[:10]
        recommendations['songs'] = SongSerializer(trending_songs, many=True).data

    # -------------------- Trending Albums --------------------
    trending_albums = Album.objects.annotate(song_count=Count('songs')).order_by('-song_count')[:5]
    recommendations['albums'] = AlbumSerializer(trending_albums, many=True).data

    # -------------------- Public Playlists --------------------
    trending_playlists = Playlist.objects.filter(privacy='public').annotate(song_count=Count('songs')).order_by(
        '-song_count')[:5]
    recommendations['playlists'] = PlaylistSerializer(trending_playlists, many=True).data

    # -------------------- Popular Artists --------------------
    trending_artists = User.objects.filter(user_profile__role='artists').annotate(
        popularity=Count('album_artist__songs')
    ).order_by('-popularity')[:5]
    recommendations['artists'] = ArtistSerializer(trending_artists, many=True).data

    return Response(recommendations)
