import uuid
from django.db import models


class Bookmark(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('auth.User', models.CASCADE)
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    anchor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return str(self.uuid)

    @property
    def timestamp(self):
        return self.created_at.timestamp()
    
    def location(self):
        return f'{self.book.slug}/{self.anchor}'
    
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
            
            
                
