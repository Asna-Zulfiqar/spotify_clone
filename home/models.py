from django.contrib.auth import get_user_model
from django.db import models
from music.models import Song
from playlists.models import Playlist

User = get_user_model()


class RecentlyPlayed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=True, blank=True)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, null=True, blank=True)
    played_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user} - {self.song or self.playlist}"
