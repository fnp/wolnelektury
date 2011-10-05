from django.conf import settings
from django.test import TestCase
import shutil
import tempfile
from slughifi import slughifi

class WLTestCase(TestCase):
    """
        Generic base class for tests. Adds settings freeze and clears MEDIA_ROOT.
    """
    def setUp(self):
        self._MEDIA_ROOT, settings.MEDIA_ROOT = settings.MEDIA_ROOT, tempfile.mkdtemp(prefix='djangotest_')
        settings.NO_BUILD_PDF = settings.NO_BUILD_EPUB = settings.NO_BUILD_TXT = True

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT, True)
        settings.MEDIA_ROOT = self._MEDIA_ROOT

class PersonStub(object):

    def __init__(self, first_names, last_name):
        self.first_names = first_names
        self.last_name = last_name


class BookInfoStub(object):

    def __init__(self, **kwargs):
        self.__dict = kwargs

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self.__dict[key] = value
        return object.__setattr__(self, key, value)

    def __getattr__(self, key):
        return self.__dict[key]

    def to_dict(self):
        return dict((key, unicode(value)) for key, value in self.__dict.items())


def info_args(title):
    """ generate some keywords for comfortable BookInfoCreation  """
    slug = unicode(slughifi(title))
    return {
        'title': unicode(title),
        'slug': slug,
        'url': u"http://wolnelektury.pl/example/%s" % slug,
        'about': u"http://wolnelektury.pl/example/URI/%s" % slug,
    }
