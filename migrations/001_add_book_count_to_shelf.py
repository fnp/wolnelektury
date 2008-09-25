from django.core.management import setup_environ
import settings

setup_environ(settings)

from catalogue.models import Tag, Book
from django.db import connection

query = 'ALTER TABLE catalogue_tag ADD COLUMN book_count integer NOT NULL DEFAULT 0'

cursor = connection.cursor()
cursor.execute(query)

for shelf in Tag.objects.filter(category='set'):
    shelf.book_count = len(Book.tagged.with_all(shelf))
    shelf.save()
