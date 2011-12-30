# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import with_statement

import random
import time
from base64 import urlsafe_b64encode

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponsePermanentRedirect
from django.core.files.uploadedfile import UploadedFile
from django.core.files.base import File
from django.core.files.storage import DefaultStorage
from django.utils.hashcompat import sha_constructor
from django.conf import settings
from celery.task import task
from os import mkdir, path, unlink
from errno import EEXIST, ENOENT
from fcntl import flock, LOCK_EX
from zipfile import ZipFile

from reporting.utils import read_chunks
from celery.task import task
import catalogue.models

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


class LockFile(object):
    """
    A file lock monitor class; createas an ${objname}.lock
    file in directory dir, and locks it exclusively.
    To be used in 'with' construct.
    """
    def __init__(self, dir, objname):
        self.lockname = path.join(dir, objname + ".lock")

    def __enter__(self):
        self.lock = open(self.lockname, 'w')
        flock(self.lock, LOCK_EX)

    def __exit__(self, *err):
        try:
            unlink(self.lockname)
        except OSError as oe:
            if oe.errno != oe.EEXIST:
                raise oe
        self.lock.close()


@task
def create_zip(paths, zip_slug):
    """
    Creates a zip in MEDIA_ROOT/zip directory containing files from path.
    Resulting archive filename is ${zip_slug}.zip
    Returns it's path relative to MEDIA_ROOT (no initial slash)
    """
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
            zipf = ZipFile(path.join(zip_path, zip_filename), 'w')
            try:
                for arcname, p in paths:
                    if arcname is None:
                        arcname = path.basename(p)
                    zipf.write(p, arcname)
            finally:
                zipf.close()

        return 'zip/' + zip_filename


def remove_zip(zip_slug):
    """
    removes the ${zip_slug}.zip file from zip store.
    """
    zip_file = path.join(settings.MEDIA_ROOT, 'zip', zip_slug + '.zip')
    try:
        unlink(zip_file)
    except OSError as oe:
        if oe.errno != ENOENT:
            raise oe


class AttachmentHttpResponse(HttpResponse):
    """Response serving a file to be downloaded.
    """
    def __init__ (self, file_path, file_name, mimetype):
        super(AttachmentHttpResponse, self).__init__(mimetype=mimetype)
        self['Content-Disposition'] = 'attachment; filename=%s' % file_name
        self.file_path = file_path
        self.file_name = file_name

        with open(DefaultStorage().path(self.file_path)) as f:
            for chunk in read_chunks(f):
                self.write(chunk)

@task
def async_build_pdf(book_id, customizations, file_name):
    """
    A celery task to generate pdf files.
    Accepts the same args as Book.build_pdf, but with book id as first parameter
    instead of Book instance
    """
    book = catalogue.models.Book.objects.get(id=book_id)
    print "will gen %s" % DefaultStorage().path(file_name)
    if not DefaultStorage().exists(file_name):
        book.build_pdf(customizations=customizations, file_name=file_name)
    print "done."


class MultiQuerySet(object):
    def __init__(self, *args, **kwargs):
        self.querysets = args
        self._count = None
    
    def count(self):
        if not self._count:
            self._count = sum(len(qs) for qs in self.querysets)
        return self._count
    
    def __len__(self):
        return self.count()
        
    def __getitem__(self, item):
        try:
            indices = (offset, stop, step) = item.indices(self.count())
        except AttributeError:
            # it's not a slice - make it one
            return self[item : item + 1][0]
        items = []
        total_len = stop - offset
        for qs in self.querysets:
            if len(qs) < offset:
                offset -= len(qs)
            else:
                items += list(qs[offset:stop])
                if len(items) >= total_len:
                    return items
                else:
                    offset = 0
                    stop = total_len - len(items)
                    continue