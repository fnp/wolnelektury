# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import datetime
import os
import os.path
import re
import sqlite3
from django.core.management.base import BaseCommand

from api.helpers import timestamp
from api.settings import MOBILE_INIT_DB
from catalogue.models import Book, Tag


class Command(BaseCommand):
    help = 'Creates an initial SQLite file for the mobile app.'

    def handle(self, **options):
        # those should be versioned
        last_checked = timestamp(datetime.now())
        db = init_db(last_checked)
        for b in Book.objects.all():
            add_book(db, b)
        for t in Tag.objects.exclude(
                category__in=('book', 'set', 'theme')).exclude(items=None):
            # only add non-empty tags
            add_tag(db, t)
        db.commit()
        db.close()
        current(last_checked)


def pretty_size(size):
    """ Turns size in bytes into a prettier string.

        >>> pretty_size(100000)
        '97 KiB'
    """
    if not size:
        return None
    units = ['B', 'KiB', 'MiB', 'GiB']
    size = float(size)
    unit = units.pop(0)
    while size > 1000 and units:
        size /= 1024
        unit = units.pop(0)
    if size < 10:
        return "%.1f %s" % (size, unit)
    return "%d %s" % (size, unit)


    if not isinstance(value, unicode):
        value = unicode(value, 'utf-8')

    # try to replace chars
    value = re.sub('[^a-zA-Z0-9\\s\\-]{1}', replace_char, value)
    value = value.lower()
    value = re.sub(r'[^a-z0-9{|}]+', '~', value)

    return value.encode('ascii', 'ignore')



def init_db(last_checked):
    if not os.path.isdir(MOBILE_INIT_DB):
        os.makedirs(MOBILE_INIT_DB)
    db = sqlite3.connect(os.path.join(MOBILE_INIT_DB, 'initial.db-%d' % last_checked))

    schema = """
CREATE TABLE book (
    id INTEGER PRIMARY KEY, 
    title VARCHAR,
    cover VARCHAR,
    html_file VARCHAR, 
    html_file_size INTEGER, 
    parent INTEGER,
    parent_number INTEGER,

    sort_key VARCHAR,
    pretty_size VARCHAR,
    authors VARCHAR,
    _local BOOLEAN
);
CREATE INDEX IF NOT EXISTS book_title_index ON book (sort_key);
CREATE INDEX IF NOT EXISTS book_title_index ON book (title);
CREATE INDEX IF NOT EXISTS book_parent_index ON book (parent);

CREATE TABLE tag (
    id INTEGER PRIMARY KEY, 
    name VARCHAR, 
    category VARCHAR, 
    sort_key VARCHAR, 
    books VARCHAR);
CREATE INDEX IF NOT EXISTS tag_name_index ON tag (name);
CREATE INDEX IF NOT EXISTS tag_category_index ON tag (category);
CREATE INDEX IF NOT EXISTS tag_sort_key_index ON tag (sort_key);

CREATE TABLE state (last_checked INTEGER);
"""

    db.executescript(schema)
    db.execute("INSERT INTO state VALUES (:last_checked)", locals())
    return db


def current(last_checked):
    target = os.path.join(MOBILE_INIT_DB, 'initial.db')
    if os.path.lexists(target):
        os.unlink(target)
    os.symlink(
        'initial.db-%d' % last_checked,
        target,
    )



book_sql = """
    INSERT INTO book 
        (id, title, cover, html_file,  html_file_size, parent, parent_number, sort_key, pretty_size, authors) 
    VALUES 
        (:id, :title, :cover, :html_file, :html_file_size, :parent, :parent_number, :sort_key, :size_str, :authors);
"""
book_tag_sql = "INSERT INTO book_tag (book, tag) VALUES (:book, :tag);"
tag_sql = """
    INSERT INTO tag
        (id, category, name, sort_key, books)
    VALUES
        (:id, :category, :name, :sort_key, :book_ids);
"""
categories = {'author': 'autor',
              'epoch': 'epoka',
              'genre': 'gatunek',
              'kind': 'rodzaj',
              'theme': 'motyw'
              }


def add_book(db, book):
    id = book.id
    title = book.title
    if book.html_file:
        html_file = book.html_file.url
        html_file_size = book.html_file.size
    else:
        html_file = html_file_size = None
    if book.cover:
        cover = book.cover.url
    else:
        cover = None
    parent = book.parent_id
    parent_number = book.parent_number
    sort_key = book.sort_key
    size_str = pretty_size(html_file_size)
    authors = ", ".join(t.name for t in book.tags.filter(category='author'))
    db.execute(book_sql, locals())


def add_tag(db, tag):
    id = tag.id
    category = categories[tag.category]
    name = tag.name
    sort_key = tag.sort_key

    books = Book.tagged_top_level([tag])
    book_ids = ','.join(str(b.id) for b in books)
    db.execute(tag_sql, locals())
