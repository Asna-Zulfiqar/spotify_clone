from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from music.models import LikeSong, UnlikeSong
from music.serializers import LikeSongSerializer, UnlikeSongSerializer
from music.utils import update_counts


class LikeSongView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LikeSongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        song = serializer.validated_data['song']
        user = request.user

        if LikeSong.objects.filter(user=user, song=song).exists():
            return Response({'message': 'You have already liked this Song.'}, status=status.HTTP_400_BAD_REQUEST)

        LikeSong.objects.create(user=user, song=song)
        song_ins = UnlikeSong.objects.filter(user=user, song=song).first()
        if song_ins:
            song_ins.delete()

        update_counts(song)
        return Response({'message': 'You have successfully liked this song.'}, status=status.HTTP_200_OK)


class UnlikeSongView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UnlikeSongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        song = serializer.validated_data['song']
        user = request.user

        if UnlikeSong.objects.filter(user=user, song=song).exists():
            return Response({'message': 'You have already unliked this song.'}, status=status.HTTP_400_BAD_REQUEST)

        UnlikeSong.objects.create(user=user, song=song)
        song_ins = LikeSong.objects.filter(user=user, song=song).first()
        if song_ins:
            song_ins.delete()

        update_counts(song)
        return Response({'message': 'You have successfully unliked this song.'})