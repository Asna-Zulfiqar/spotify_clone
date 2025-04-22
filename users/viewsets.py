from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.utils.timezone import now
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import ArtistRequest
from users.permission import IsAdmin
from users.serializers import UserSerializer, LoginSerializer, UserProfileSerializer, ArtistRequestResponseSerializer, \
    ArtistRequestSerializer, UpdatePasswordSerializer, UserResponseSerializer

User = get_user_model()

class UserViewSet(ModelViewSet):
    queryset = User.objects.all().select_related('user_profile')
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = UserResponseSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': serializer.data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'message':'Login Successfully', 'token': token.key, 'user': UserSerializer(user).data})
        return Response({'error': 'Invalid Credentials'}, status=400)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def view_profile(self, request):
        user = request.user
        profile = user.user_profile
        profile_data = UserProfileSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=profile_data)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        user_profile = request.user.user_profile
        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def update_password(self, request):
        serializer = UpdatePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"detail": "Password updated successfully."},status=status.HTTP_200_OK,)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        user = request.user
        token = Token.objects.get(user=user)
        token.delete()
        return Response({"details":"Logout Successfully"}, status=status.HTTP_200_OK)



class ArtistRequestViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the appropriate serializer based on action"""
        if self.action in ['list', 'retrieve', 'approve', 'reject']:
            return ArtistRequestResponseSerializer
        return ArtistRequestSerializer

    def get_queryset(self):
        """Users see their own requests, admins see all"""
        if self.request.user.is_staff:
            return ArtistRequest.objects.all()
        return ArtistRequest.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        description = request.data.get('description', '')

        if ArtistRequest.objects.filter(user=user, status='pending').exists():
            return Response({"message": "You already have a pending request."}, status=400)

        artist_request = ArtistRequest.objects.create(user=user, description=description , status='Pending')
        return Response(ArtistRequestResponseSerializer(artist_request).data, status=201)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        """
        Admin updates the status of an artist request.
        """
        artist_request = self.get_object()
        if artist_request.status != 'Pending':
            return Response(
                {"error": "This request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data.get("status")
        if new_status not in ["Approved", "Rejected"]:
            return Response(
                {"error": "Invalid status. Use 'Approved' or 'Rejected'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status == "Approved":
            user = artist_request.user

            user.user_profile.role = 'artists'
            user.user_profile.save()

            users_group = Group.objects.get(name="Users")
            artists_group, _ = Group.objects.get_or_create(name="Artists")
            user.groups.remove(users_group)
            user.groups.add(artists_group)

            artist_request.status = "Approved"
            artist_request.is_approved = True
            artist_request.approved_at = now()
        else:
            artist_request.status = "Rejected"

        artist_request.save()

        return Response(
            ArtistRequestResponseSerializer(artist_request).data,
            status=status.HTTP_200_OK
        )