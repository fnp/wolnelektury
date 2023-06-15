# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from wolnelektury.settings import *

THUMBNAIL_BACKEND = 'wolnelektury.test_utils.DummyThumbnailBackend'
CATALOGUE_GET_MP3_LENGTH = 'catalogue.test_utils.get_mp3_length'
MEDIA_URL = '/media/'

SEARCH_CONFIG = 'english'
SEARCH_CONFIG_SIMPLE = 'simple'
SEARCH_USE_UNACCENT = False
