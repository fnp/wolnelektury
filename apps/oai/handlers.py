
from oaipmh import server, common
from catalogue.models import Book, Tag
from api.models import Deleted
from librarian.dcparser import BookInfo
from django.contrib.contenttypes.models import ContentType


class Catalogue(common.ResumptionOAIPMH):
    def __init__(self):
        super(Catalogue, self).__init__()

    def metadata(self, book):
        bi = BookInfo.from_file(book.xml_file)
        meta = {}
        for field in bi.FIELDS:
            dc_field = field.uri.split('}')[1]
            value = getattr(bi, dc_field.name)
            if isinstance(value,list):
                value = ';'.join(map(unicode, value))
            else:
                value = unicode(value)
            meta["dc:"+dc_field] = value
        return meta

    def record_for_book(self, book):
        header = common.Header(book.slug, book.changed_at, [], False)
        meta = common.Metadata(self.metadata(book))
        about = None
        return header, meta, about

    def getRecord(self, record, **kw):
        """
Returns (header, metadata, about) for given record.
        """
        slug = kw['record']
        try:
            book = Book.objects.get(slug=slug)
            return self.record_for_book(book)
        except Book.DoesNotExist, e:
            book_type = ContentType.objects.get_for_model(Book)
            deleted_book = Deleted.objects.filter(content_type=book_type,
                                                  slug=slug)
            header = common.Header(deleted_book.slug,
                                   deleted_book.deleted_at,
                                   [], True)
            meta = common.Metadata({})
            return header, meta, None # None for about.
                                   

        
    def listRecords(self, **kw):
        """
can get a resumptionToken kw.
returns result, token
        """
        return [self.record_for_book(book) for book in Book.objects.all()]
            
