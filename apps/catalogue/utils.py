# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import random
import time
from base64 import urlsafe_b64encode

from django.core.files.uploadedfile import UploadedFile
from django.utils.hashcompat import sha_constructor
from django.conf import settings

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
    """ used for joined EPUBs """

    def __init__(self, book):
        self.book = book
        
    def by_slug(self, slug):
        if slug == self.book.slug:
            return self.book.xml_file
        else:
            return Book.objects.get(slug=slug).xml_file
