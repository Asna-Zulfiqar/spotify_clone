from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from home.utils import search, user_recommendations


class SearchAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('query', None)
        type = request.query_params.get('type', None)

        if not query:
            return Response(
                {"error": "Search query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return search(query, type)


class RecommendationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return user_recommendations(user)
