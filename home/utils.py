from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count,F, Sum
from django.utils import timezone
from rest_framework.response import Response
from home.models import RecentlyPlayed
from music.models import Song, Album, LikeSong, UnlikeSong
from music.serializers import SongSerializer, AlbumResponseSerializer, AlbumSerializer
from playlists.models import Playlist
from playlists.serializers import PlaylistSerializer
from users.serializers import UserResponseSerializer
from django.contrib.postgres.search import SearchVector

User = get_user_model()


def add_to_recently_played(user, song=None, playlist=None):

    if RecentlyPlayed.objects.filter(user=user).count() >= 6:
        oldest = RecentlyPlayed.objects.filter(user=user).order_by('played_at').first()
        if oldest:
            oldest.delete()

    if song:
        RecentlyPlayed.objects.update_or_create(
            user=user,
            song=song,
            defaults={'played_at': timezone.now()}
        )
    elif playlist:
        RecentlyPlayed.objects.update_or_create(
            user=user,
            playlist=playlist,
            defaults={'played_at': timezone.now()}
        )



def search(query, type):
    results = {}

    # SONGS
    if not type or type == 'songs':
        songs = (
            Song.objects
                .annotate(
                    search=SearchVector(
                        'title',
                        'album__title',
                        'album__artist__user_profile__display_name',
                    )
                )
                .filter(search=query)
                .select_related('album', 'album__artist', 'album__artist__user_profile')
                .prefetch_related('genre', 'featured_artists__user_profile')
        )
        results['songs'] = SongSerializer(songs, many=True).data

    # ALBUMS
    if not type or type == 'albums':
        albums = (
            Album.objects
                .annotate(
                    search=SearchVector(
                        'title',
                        'artist__user_profile__display_name',
                    )
                )
                .filter(search=query)
                .select_related('artist__user_profile')
                .prefetch_related('songs')
        )
        results['albums'] = AlbumResponseSerializer(albums, many=True).data

    # ARTISTS
    if not type or type == 'artists':
        artists = (
            User.objects
                .filter(user_profile__role='artists')
                .annotate(
                    search=SearchVector(
                        'first_name',
                        'last_name',
                        'user_profile__display_name',
                    )
                )
                .filter(search=query)
                .distinct()
                .select_related('user_profile')
        )
        results['artists'] = UserResponseSerializer(artists, many=True).data

    # PLAYLISTS
    if not type or type == 'playlists':
        playlists = (
            Playlist.objects
                .annotate(
                    search=SearchVector(
                        'name',
                        'user__user_profile__display_name',
                    )
                )
                .filter(search=query, privacy='public')
                .select_related('user__user_profile')
                .prefetch_related('songs')
        )
        results['playlists'] = PlaylistSerializer(playlists, many=True).data

    return Response(results)

def explore_page_recommendations(user):
    display_name = user.user_profile.display_name
    explore = {}

    # ===  PERSONALIZED SECTIONS ===

    liked_ids = list(LikeSong.objects.filter(user=user).values_list('song_id', flat=True))
    disliked_ids = list(UnlikeSong.objects.filter(user=user).values_list('song_id', flat=True))
    top_genres = (
        Song.objects.filter(id__in=liked_ids)
        .prefetch_related('genre')
        .values('genre__id')
        .annotate(genre_count=Count('genre__id'))
        .order_by('-genre_count')[:3]
    )

    top_genre_ids = [genre['genre__id'] for genre in top_genres]
    # Made For You Section
    if liked_ids:
        made_for_you = (
            Song.objects.filter(genre__id__in=top_genre_ids)
            .exclude(id__in=liked_ids + disliked_ids)
            .select_related('album', 'album__artist')
            .prefetch_related('genre')
            .order_by('-plays_count')
            .distinct()[:6]
        )

        explore['made_for_you'] = {
            'title': f'Made for {display_name}',
            'items': SongSerializer(made_for_you, many=True).data
        }

    # Recommended Today Section
    recommended_today = (
        Song.objects
        .exclude(id__in=liked_ids + disliked_ids)
        .order_by('-released_date')
        .select_related('album', 'album__artist')
        .prefetch_related('genre')
        .distinct()[:6]
    )
    explore['recommended_today'] = {
        'title': 'Recommended for Today',
        'items': SongSerializer(recommended_today, many=True).data
    }

    # Based On Your Recent Listening Section
    recommended_playlists = Playlist.objects.filter(songs__genre__in=top_genre_ids, privacy='public').distinct()[:6]
    explore['recommended_playlists'] = {
        'title': 'Based On Your Recent Listening',
        'items': PlaylistSerializer(recommended_playlists, many=True).data
    }

    # Recently Played Section
    recently_played = RecentlyPlayed.objects.filter(user=user).order_by('-played_at')
    recent_songs = [entry.song for entry in recently_played if entry.song]
    recent_playlists = [entry.playlist for entry in recently_played if entry.playlist]

    if recent_songs:
        explore['recently_played_songs'] = {
            'title': 'Recently Played Songs',
            'items': SongSerializer(recent_songs, many=True).data
        }

    if recent_playlists:
        explore['recently_played_playlists'] = {
            'title': 'Recently Played Playlists',
            'items': PlaylistSerializer(recent_playlists, many=True).data
        }
    # === TRENDING CONTENT ===

    # Popular Albums
    popular_albums = (
        Album.objects
        .annotate(total_plays=Sum('songs__plays_count'))
        .filter(total_plays__gt=0)
        .order_by('-total_plays')
        .select_related('artist')
        .prefetch_related('songs')[:6]
    )

    explore['popular_albums'] = {
        'title': 'Popular Albums',
        'items': AlbumSerializer(popular_albums, many=True).data
    }

    # Popular Artists Section
    popular_artists = (
        User.objects
        .filter(album_artist__songs__isnull=False)
        .annotate(total_plays=Sum('album_artist__songs__plays_count'))
        .filter(total_plays__gt=0)
        .order_by('-total_plays')
        .distinct()[:6]
    )

    if popular_artists:
        explore['popular_artists'] = {
            'title': 'Artist You May Like',
            'items': UserResponseSerializer(popular_artists, many=True).data
        }

    # Trending Songs Section
    trending_window = timezone.now().date() - timedelta(days=30)

    trending_songs = (
        Song.objects
        .filter(released_date__gte=trending_window)
        .annotate(total_engagement=F('plays_count') + F('likes'))
        .order_by('-total_engagement')
        .select_related('album', 'album__artist')
        .prefetch_related('genre')
        [:6]
    )

    explore['trending_songs'] = {
        'title': 'Trending Songs',
        'items': SongSerializer(trending_songs, many=True).data
    }

    # Trending Playlists Section
    trending_playlists = (
        Playlist.objects
        .annotate(total_plays=Sum('songs__plays_count'))
        .filter(total_plays__gt=0, privacy='public')
        .order_by('-total_plays')
        .distinct()[:6]
    )

    explore['trending_playlists'] = {
        'title': 'Popular Radio',
        'items': PlaylistSerializer(trending_playlists, many=True).data
    }
    return Response(explore)


