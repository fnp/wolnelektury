#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.management import setup_environ
from wolnelektury import settings
import sys
from os.path import abspath, join, dirname, splitext
import os

# Add apps and lib directories to PYTHONPATH
sys.path.insert(0, abspath(join(dirname(__file__), 'apps')))
sys.path.insert(0, abspath(join(dirname(__file__), 'lib')))

setup_environ(settings)

from catalogue.models import Book
from mutagen import easyid3
from slughifi import slughifi

chosen_book_slugs = set()

for file_name in os.listdir('mp3'):
    base_name, ext = splitext(file_name)
    if ext != '.mp3':
        continue
    
    audio = easyid3.EasyID3(join('mp3', file_name))
    title = audio['title'][0]
    artist = title.split(',', 1)[0].strip()
    artist_slug = slughifi(artist)
    title_part = slughifi(title.rsplit(',', 1)[1].strip())
    
    print "--------------------"
    print "File: %s" % file_name
    print "Title: %s" % title
    print
    print "Matching books:"
    
    matching_books = [book for book in Book.tagged.with_all(artist_slug) if book.slug not in chosen_book_slugs]
    matching_books = [book for book in matching_books if title_part in book.slug]

    if len(matching_books) > 1:
        for i, book in enumerate(matching_books):
            print "%d: %s (%s)" % (i, book.title, ', '.join(tag.slug for tag in book.tags))
        print
        i = int(input("Choose which book is read in this file:"))
    elif len(matching_books) == 1:
        i = 0
    else:
        print "Skipping %s: No matching book found" % file_name
        continue
    
    print "You chose %d (%s)" % (i, matching_books[i].slug)
    
    chosen_book_slugs.add(matching_books[i].slug)
    os.rename(join('mp3', file_name), join('new_mp3', matching_books[i].slug + '.mp3'))
    os.rename(join('oggvorbis', base_name + '.ogg'), join('new_ogg', matching_books[i].slug + '.ogg'))
    
    