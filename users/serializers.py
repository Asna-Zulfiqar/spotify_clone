from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.contrib.auth.models import  Group

from music.models import Album
from music.serializers import AlbumResponseSerializer
from users.models import UserProfile , ArtistRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for Registering new User.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8},
                        'email': {'required': True}}

    def create(self, validated_data):
        validated_data['username'] = validated_data.get('email')
        user = User.objects.create_user(**validated_data)
        users_group, created = Group.objects.get_or_create(name="Users")
        user.groups.add(users_group)
        UserProfile.objects.create(user=user , role='users')
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    albums = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'albums' ,'display_name', 'bio' , 'date_of_birth' , 'created_at', 'profile_picture' , 'role']

    def get_albums(self, obj):
        """Return all albums only if the user is an artist."""
        if obj.user.groups.filter(name="Artists").exists():
            return AlbumResponseSerializer(Album.objects.filter(artist=obj.user), many=True).data
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.user.groups.filter(name="Artists").exists():
            data.pop("albums", None)
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ArtistRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistRequest
        fields = ['id', 'user', 'description']

class ArtistRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistRequest
        fields = ['id', 'user', 'description' , 'status' , 'is_approved' , 'created_at', 'approved_at']