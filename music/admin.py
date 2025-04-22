from django.contrib import admin
from music.models import *

admin.site.register(Genre)

class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist','total_songs','release_date']

admin.site.register(Album, AlbumAdmin)

class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'album', 'plays_count', 'released_date' , 'likes' , 'dislikes']

admin.site.register(Song, SongAdmin)

admin.site.register(LikeSong)
admin.site.register(UnlikeSong)
admin.site.register(Follow)