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

    @classmethod
    def create_from_data(cls, user, data):
        if data.get('location'):
            return cls.get_by_location(user, data['location'], create=True)
        elif data.get('book') and data.get('anchor'):
            return cls.objects.create(user=user, book=data['book'], anchor=data['anchor'])
    
    @property
    def timestamp(self):
        return self.updated_at.timestamp()
    
    def location(self):
        return f'{self.book.slug}/{self.anchor}'

    @classmethod
    def get_by_location(cls, user, location, create=False):
        Book = apps.get_model('catalogue', 'Book')
        try:
            slug, anchor = location.split('/')
        except:
            return None
        instance = cls.objects.filter(
            user=user,
            book__slug=slug,
            anchor=anchor
        ).first()
        if instance is None and create:
            try:
                book = Book.objects.get(slug=slug)
            except Book.DoesNotExist:
                return None
            instance = cls.objects.create(
                user=user,
                book=book,
                anchor=anchor
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
            
            
                
