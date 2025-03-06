from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from music.models import Album, Song
from music.serializers import AlbumSerializer, AlbumResponseSerializer, SongSerializer, SongResponseSerializer


class AlbumViewSet(ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumResponseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        album = serializer.save(artist=request.user)
        response_serializer = AlbumResponseSerializer(album)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AlbumSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        album = serializer.save()
        response_serializer = AlbumResponseSerializer(album)
        return Response(response_serializer.data, status=status.HTTP_200_OK)



class SongViewSet(ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongResponseSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        serializer = SongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        song = serializer.save()
        response_serializer = SongResponseSerializer(song)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SongSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        song = serializer.save()
        response_serializer = SongResponseSerializer(song)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

