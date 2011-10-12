
from django.conf import settings
from lucene import SimpleFSDirectory, IndexWriter
import os


class BookSearch(object):
    def __init__(self):
        if not os.exists(settings.SEARCH_INDEX):
            os.mkdir(settings.SEARCH_INDEX)
        self.store = IndexWriter(store, )
                         
