# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from catalogue.models import Tag, Book

class Migration:
    
    def forwards(self):
        "Write your forwards migration here"
        for tag in Tag.objects.filter(user__isnull=False):
            books = Tag.intermediary_table_model.objects.get_intersection_by_model(Book, [tag])
            tag.book_count = len(books)
            tag.save()
    
    def backwards(self, orm):
        "Write your backwards migration here"
        pass
