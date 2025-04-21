from rest_framework import status
from rest_framework.response import Response
from music.models import Song
from playlists.models import Playlist


def add_or_remove_song_to_playlist(user, playlist_id, song_id):
    try:
        playlist = Playlist.objects.filter(id=playlist_id, user=user).first()
        if not playlist:
            return Response({'error': 'Playlist not found'}, status=status.HTTP_404_NOT_FOUND)

        song = Song.objects.filter(id=song_id).first()
        if not song:
            return Response({'error': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        if playlist.songs.filter(id=song_id).exists():
            playlist.songs.remove(song)
            playlist.total_songs -= 1
            playlist.save()
            return Response({'message': 'Song Removed from Playlist'}, status=status.HTTP_200_OK)

        playlist.songs.add(song)
        playlist.total_songs += 1
        playlist.save()

        return Response({'message': f'Song "{song}" added successfully to Playlist "{playlist}"'},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
