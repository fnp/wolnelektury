# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import with_statement

import random
import time
from base64 import urlsafe_b64encode

from django.core.files.uploadedfile import UploadedFile
from django.utils.hashcompat import sha_constructor
from django.conf import settings
from celery.task import task
from os import mkdir, path, unlink
from errno import EEXIST
from fcntl import flock, LOCK_EX
from zipfile import ZipFile

from librarian import DocProvider


# Use the system (hardware-based) random number generator if it exists.
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_SESSION_KEY = 18446744073709551616L     # 2 << 63


def get_random_hash(seed):
    sha_digest = sha_constructor('%s%s%s%s' %
        (randrange(0, MAX_SESSION_KEY), time.time(), unicode(seed).encode('utf-8', 'replace'),
        settings.SECRET_KEY)).digest()
    return urlsafe_b64encode(sha_digest).replace('=', '').replace('_', '-').lower()


def split_tags(tags):
    result = {}
    for tag in tags:
        result.setdefault(tag.category, []).append(tag)
    return result


class ExistingFile(UploadedFile):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        return super(ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass


class BookImportDocProvider(DocProvider):
    """Used for joined EPUB and PDF files."""

    def __init__(self, book):
        self.book = book

    def by_slug(self, slug):
        if slug == self.book.slug:
            return self.book.xml_file
        else:
            return type(self.book).objects.get(slug=slug).xml_file


class LockFile(object):
    def __init__(self, dir, objname):
        self.lockname = path.join(dir, objname + ".lock")

    def __entry__(self):
        self.lock = open(self.lockname, 'w')
        flock(self.lock, LOCK_EX)

    def __exit__(self, *err):
        self.lock.close()
        unlink(self.lockname)


def create_zip(paths, zip_slug):
    # directory to store zip files
    zip_path = path.join(settings.MEDIA_ROOT, 'zip')

    try:
        mkdir(zip_path)
    except OSError as oe:
        if oe.errno != EEXIST:
            raise oe
    zip_filename = zip_slug + ".zip"

    with LockFile(zip_path, zip_slug):
        if not path.exists(path.join(zip_path, zip_filename)):
            with ZipFile(path.join(zip_path, zip_filename), 'w') as zipf:
                for p in paths:
                    zipf.write(p, path.basename(p))

        return 'zip/' + zip_filename


def remove_zip(zip_slug):
    zip_file = path.join(settings.MEDIA_ROOT, 'zip', zip_slug + '.zip')
    try:
        unlink(zip_file)
    except OSError as oe:
        if oe.errno != EEXIST:
            raise oe


@task
def create_zip_task(*args):
    return create_zip(*args)
