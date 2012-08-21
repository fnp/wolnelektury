# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.test import TestCase
from django.test.utils import override_settings
import tempfile
from slughifi import slughifi
from librarian import WLURI

@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(prefix='djangotest_'),
    CATALOGUE_DONT_BUILD={'pdf', 'mobi', 'epub', 'txt', 'fb2', 'cover'},
    NO_SEARCH_INDEX = True,
    CELERY_ALWAYS_EAGER = True,
    CACHES={
            'api': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
            'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
            'permanent': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'},
        },
)
class WLTestCase(TestCase):
    """
        Generic base class for tests. Adds settings freeze and clears MEDIA_ROOT.
    """
    longMessage = True


class PersonStub(object):

    def __init__(self, first_names, last_name):
        self.first_names = first_names
        self.last_name = last_name

    def readable(self):
        return " ".join(self.first_names + (self.last_name,))


class BookInfoStub(object):
    _empty_fields = ['cover_url', 'variant_of']
    # allow single definition for multiple-value fields
    _salias = {
        'authors': 'author',
    }

    def __init__(self, **kwargs):
        self.__dict = kwargs

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self.__dict[key] = value
        return object.__setattr__(self, key, value)

    def __getattr__(self, key):
        try:
            return self.__dict[key]
        except KeyError:
            if key in self._empty_fields:
                return None
            elif key in self._salias:
                return [getattr(self, self._salias[key])]
            else:
                raise

    def to_dict(self):
        return dict((key, unicode(value)) for key, value in self.__dict.items())


def info_args(title, language=None):
    """ generate some keywords for comfortable BookInfoCreation  """
    slug = unicode(slughifi(title))
    if language is None:
        language = u'pol'
    return {
        'title': unicode(title),
        'url': WLURI.from_slug(slug),
        'about': u"http://wolnelektury.pl/example/URI/%s" % slug,
        'language': language,
    }
