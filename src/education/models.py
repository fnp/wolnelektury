import json
from django.conf import settings
from django.db import models
from requests_oauthlib import OAuth2Session


YOUTUBE_SCOPE = [
    'https://www.googleapis.com/auth/youtube',
]
YOUTUBE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
YOUTUBE_TOKEN_URL = 'https://oauth2.googleapis.com/token'


class Course(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.slug


class Track(models.Model):
    course = models.ForeignKey(Course, models.CASCADE)


class Tag(models.Model):
    name = models.CharField(max_length=255)
    

class Item(models.Model):
    course = models.ForeignKey(Course, models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    youtube_id = models.CharField(max_length=255, blank=True)
    order = models.IntegerField(default=0, blank=True)

    class Meta:
        ordering = ('order',)
    
    def __str__(self):
        return self.title


class YPlaylist(models.Model):
    course = models.ForeignKey(Course, models.CASCADE)
    youtube_id = models.CharField(max_length=255, blank=True)

    def save(self):
        super().save()
        self.download()
    
    def download(self):
        response = YouTubeToken.objects.first().call(
            "GET",
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params={
                'part': 'snippet',
                'playlistId': self.youtube_id,
                'maxResults': 50,
            },
        )
        data = response.json()
        for item in data['items']:
            self.course.item_set.update_or_create(
                youtube_id=item['snippet']['resourceId']['videoId'],
                defaults={
                    'title': item['snippet']['title'],
                    'order': item['snippet']['position'],
                }
            )



class YouTubeToken(models.Model):
    token = models.TextField()

    def token_updater(self, token):
        self.token = json.dumps(token)
        self.save()

    def get_session(self):
        return OAuth2Session(
            client_id=settings.YOUTUBE_CLIENT_ID,
            auto_refresh_url=YOUTUBE_TOKEN_URL,
            token=json.loads(self.token),
            auto_refresh_kwargs={'client_id':settings.YOUTUBE_CLIENT_ID,'client_secret':settings.YOUTUBE_CLIENT_SECRET},
            token_updater=self.token_updater
        )

    def call(self, method, url, params=None, json=None, data=None, resumable_file_path=None):
        params = params or {}
        if resumable_file_path:
            params['uploadType'] = 'resumable'
            file_size = os.stat(resumable_file_path).st_size

        session = self.get_session()
        response = session.request(
            method=method,
            url=url,
            json=json,
            data=data,
            params=params,
            headers={
                'X-Upload-Content-Length': str(file_size),
                'x-upload-content-type': 'application/octet-stream',
            } if resumable_file_path else {}
        )
        response.raise_for_status()
        return response

