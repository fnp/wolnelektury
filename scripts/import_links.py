import sys
sys.path.insert(0, '../apps')
sys.path.insert(0, '../lib')
sys.path.insert(0, '../wolnelektury')
sys.path.insert(0, '..')

from django.core.management import setup_environ
from wolnelektury import settings
import sys

setup_environ(settings)

from catalogue.models import Book, Tag


def import_links(file_name, attribute):
    for line in file(file_name):
        slug, link = line.split()
        link = link.strip('\n')
        try:
            book = Book.objects.get(slug=slug)
            setattr(book, attribute, link)
            book.save()
            print 'Link %s for book %s added!' % (link, book)
        except Book.DoesNotExist:
            try:
                tag = Tag.objects.get(slug=slug)
                setattr(tag, attribute, link)
                tag.save()
                print 'Link %s for tag %s added!' % (link, tag)
            except Tag.DoesNotExist:
                print 'Invalid slug %s!' % slug


import_links('gazeta-links', 'gazeta_link')
import_links('wiki-links', 'wiki_link')
