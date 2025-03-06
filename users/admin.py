from django.contrib import admin
from users.models import *

admin.site.register(Users)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'display_name', 'date_of_birth' ,'role' ,'created_at')

admin.site.register(UserProfile, UserProfileAdmin)

class ArtistRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'is_approved', 'created_at', 'approved_at')

admin.site.register(ArtistRequest, ArtistRequestAdmin)