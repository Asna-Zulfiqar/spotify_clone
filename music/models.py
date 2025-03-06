import uuid
from django.db import models
from spotify_clone import settings

User = settings.AUTH_USER_MODEL

class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='album_artist')
    description = models.CharField(max_length=255)
    release_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to="album_covers/", blank=True, null=True)
    total_songs = models.PositiveIntegerField(default=0)
    genres = models.ManyToManyField(Genre, blank=True)

    def __str__(self):
        return self.title


class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    song_cover_image = models.ImageField(upload_to='songs/covers/', null=True, blank=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="songs" , null=True, blank=True)
    featured_artists = models.ManyToManyField(User, blank=True, related_name='featured_artists')
    duration = models.DurationField()
    CATEGORY_CHOICES = [
        ('Premium', 'Premium'),
        ('Free', 'Free'),
    ]
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=255, default='Free')
    lyrics = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, blank=True , related_name='albums')
    audio_file = models.FileField(upload_to="songs/audios/", blank=False, null=False)
    plays_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    released_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.album.artist.username if self.album and self.album.artist else 'Unknown Artist'}"

