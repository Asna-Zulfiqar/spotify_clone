from django.contrib import admin
from playlists.models import *


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'privacy', 'total_songs')

admin.site.register(Playlist, PlaylistAdmin)