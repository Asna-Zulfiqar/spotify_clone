from music.models import LikeSong, Song, UnlikeSong


def update_counts(song):
    likes = LikeSong.objects.filter(song=song).count()
    dislikes= UnlikeSong.objects.filter(song=song).count()
    Song.objects.filter(id=song.id).update(likes=likes, dislikes=dislikes)