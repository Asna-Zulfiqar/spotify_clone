import uuid
from django.contrib.auth import get_user_model
from django.db import models
from music.models import Song

User = get_user_model()

class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='user_playlist')
    name = models.CharField(max_length=255)
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private')
    ]
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    total_songs = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"