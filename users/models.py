import uuid
from django.contrib.auth.models import User, AbstractUser
from django.db import models

class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(Users, on_delete=models.CASCADE , related_name='user_profile')

    display_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USER_ROLES = [
        ('users', 'Users'),
        ('artists', 'Artists'),
    ]
    role = models.CharField(choices=USER_ROLES, max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"