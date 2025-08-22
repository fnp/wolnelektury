import uuid
from django.apps import apps
from django.db import models
from django.utils.timezone import now
from social.syncable import Syncable


class Bookmark(Syncable, models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', models.CASCADE)
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    anchor = models.CharField(max_length=100, blank=True)
    audio_timestamp = models.IntegerField(null=True, blank=True)
    mode = models.CharField(max_length=64, choices=[
        ('text', 'text'),
        ('audio', 'audio'),
    ], default='text')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    reported_timestamp = models.DateTimeField(default=now)
    deleted = models.BooleanField(default=False)

    syncable_fields = [
        'deleted', 'note',
    ]

    def __str__(self):
        return str(self.uuid)

    def save(self, *args, **kwargs):
        # TODO: placeholder.
        try:
            audio_l = self.book.get_audio_length()
        except:
            audio_l = 60
        if self.anchor:
            self.mode = 'text'
            if audio_l:
                self.audio_timestamp = audio_l * .4
        if self.audio_timestamp:
            self.mode = 'audio'
            if self.audio_timestamp > audio_l:
                self.audio_timestamp = audio_l
            if audio_l:
                self.anchor = 'f20'
        return super().save(*args, **kwargs)

    @classmethod
    def create_from_data(cls, user, data):
        if data.get('location'):
            return cls.get_by_location(user, data['location'], create=True)
        elif data.get('book') and data.get('anchor'):
            return cls.objects.create(user=user, book=data['book'], anchor=data['anchor'])
        elif data.get('book') and data.get('audio_timestamp'):
            return cls.objects.create(user=user, book=data['book'], audio_timestamp=data['audio_timestamp'])
    
    @property
    def timestamp(self):
        return self.updated_at.timestamp()
    
    def location(self):
        if self.mode == 'text':
            return f'{self.book.slug}/{self.anchor}'
        else:
            return f'{self.book.slug}/audio/{self.audio_timestamp}'

    @classmethod
    def get_by_location(cls, user, location, create=False):
        Book = apps.get_model('catalogue', 'Book')
        try:
            slug, anchor = location.split('/', 1)
        except:
            return None
        if '/' in anchor:
            try:
                mode, audio_timestamp = anchor.split('/', 1)
                assert mode == 'audio'
                audio_timestamp = int(audio_timestamp)
            except:
                return None
            anchor = ''
            instance = cls.objects.filter(
                user=user,
                book__slug=slug,
                mode=mode,
                audio_timestamp=audio_timestamp,
            ).first()
        else:
            mode = 'text'
            audio_timestamp = None
            instance = cls.objects.filter(
                user=user,
                book__slug=slug,
                mode='text',
                anchor=anchor,
            ).first()
        if instance is None and create:
            try:
                book = Book.objects.get(slug=slug)
            except Book.DoesNotExist:
                return None
            instance = cls.objects.create(
                user=user,
                book=book,
                mode=mode,
                anchor=anchor,
                audio_timestamp=audio_timestamp,
            )
        return instance
    
    def get_for_json(self):
        return {
            'uuid': self.uuid,
            'anchor': self.anchor,
            'note': self.note,
            'created_at': self.created_at,
        }


class Quote(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', models.CASCADE)
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    start_elem = models.CharField(max_length=100, blank=True)
    end_elem = models.CharField(max_length=100, blank=True)
    start_offset = models.IntegerField(null=True, blank=True)
    end_offset = models.IntegerField(null=True, blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return str(self.uuid)

    def get_for_json(self):
        return {
            'uuid': self.uuid,
            'startElem': self.start_elem,
            'endElem': self.end_elem,
            'startOffset': self.start_offset,
            'startOffset': self.end_offset,
            'created_at': self.created_at,
        }

def from_path(elem, path):
    def child_nodes(e):
        if e.text: yield (e, 'text')
        for child in e:
            if child.attrib.get('id') != 'toc':
                yield (child, None)
            if child.tail:
                yield (child, 'tail')
    while len(path) > 1:
        n = path.pop(0)
        elem = list(child_nodes(elem))[n]
    return elem
            
            
                
