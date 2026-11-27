# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from wolnelektury.settings import *

THUMBNAIL_BACKEND = 'wolnelektury.test_utils.DummyThumbnailBackend'
MEDIA_URL = '/media/'

CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
    'template_fragments': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
}
