import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import UserProfile

User = get_user_model()

class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("access_token")
        if not access_token:
            return Response({"error": "Access token is required"}, status=400)

        # Verify token with Google
        google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(google_user_info_url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Invalid access token"}, status=400)

        data = response.json()
        email = data.get("email")
        name = data.get("name")

        if not email:
            return Response({"error": "Email not found in Google response"}, status=400)

        # Get or create the user
        user, created = User.objects.get_or_create(email=email, defaults={
            "username": email.split("@")[0],
            "first_name": name.split()[0] if name else "",
            "last_name": name.split()[1] if name and len(name.split()) > 1 else "",
        })

        UserProfile.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "token": token.key
        }, status=status.HTTP_200_OK)
