from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.contrib.auth.models import  Group
from music.models import Album
from music.serializers import AlbumResponseSerializer
from playlists.models import Playlist
from users.models import UserProfile , ArtistRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
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
    my_playlists = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'display_name', 'bio' , 'date_of_birth' , 'created_at', 'profile_picture' , 'role', 'albums', 'my_playlists']

    def get_albums(self, obj):
        """Return all albums only if the user is an artist."""
        if obj.user.groups.filter(name="Artists").exists():
            return AlbumResponseSerializer(Album.objects.filter(artist=obj.user), many=True).data
        return None

    def get_my_playlists(self, obj):
        from playlists.serializers import PlaylistSerializer
        playlists=Playlist.objects.filter(user=obj.user)
        return PlaylistSerializer(playlists, many=True).data

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

class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)
    new_password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if len(new_password) < 8:
            raise serializers.ValidationError({"new_password": "Password must be at least 8 characters long."})

        if new_password != new_password_confirm:
            raise serializers.ValidationError({"new_password": "Passwords must match."})

        user = authenticate(request=self.context.get('request'), username=self.context.get('request').user.username,
                            password=current_password)
        if user is None:
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        attrs['user'] = user
        return attrs

class UserResponseSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'email', 'profile_picture']

    def get_display_name(self, obj):
        return obj.user_profile.display_name if hasattr(obj, 'user_profile') else obj.username

    def get_profile_picture(self, obj):
        if hasattr(obj, 'user_profile') and obj.user_profile.profile_picture:
            try:
                return obj.user_profile.profile_picture.url
            except ValueError:
                return None
        return None
