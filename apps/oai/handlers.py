from oaipmh import server, common, metadata, error
from catalogue.models import Book, Tag
from api.models import Deleted
from api.handlers import WL_BASE
from librarian.dcparser import BookInfo
from librarian import WLURI
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from datetime import datetime
from lxml import etree
from lxml.etree import ElementTree
from django.db.models import Q


wl_dc_reader = metadata.MetadataReader(
    fields={
    'title':       ('textList', 'rdf:RDF/rdf:Description/dc:title/text()'),
    'creator':     ('textList', 'rdf:RDF/rdf:Description/dc:creator/text()'),
    'subject':     ('textList', 'rdf:RDF/rdf:Description/dc:subject.period/text() | rdf:RDF/rdf:Description/dc:subject.type/text() | rdf:RDF/rdf:Description/dc:subject.genre/text()'),
    'description': ('textList', 'rdf:RDF/rdf:Description/dc:description/text()'),
    'publisher':   ('textList', 'rdf:RDF/rdf:Description/dc:publisher/text()'),
    'contributor': ('textList', 'rdf:RDF/rdf:Description/dc:contributor.editor/text() | rdf:RDF/rdf:Description/dc:contributor.translator/text() | rdf:RDF/rdf:Description/dc:contributor.technical_editor/text()'),
    'date':        ('textList', 'rdf:RDF/rdf:Description/dc:date/text()'),
    'type':        ('textList', 'rdf:RDF/rdf:Description/dc:type/text()'),
    'format':      ('textList', 'rdf:RDF/rdf:Description/dc:format/text()'),
    'identifier':  ('textList', 'rdf:RDF/rdf:Description/dc:identifier.url/text()'),
    'source':      ('textList', 'rdf:RDF/rdf:Description/dc:source/text()'),
    'language':    ('textList', 'rdf:RDF/rdf:Description/dc:language/text()'),
    #    'relation':    ('textList', 'rdf:RDF/rdf:Description/dc:relation/text()'),
    #    'coverage':    ('textList', 'rdf:RDF/rdf:Description/dc:coverage/text()'),
    'rights':      ('textList', 'rdf:RDF/rdf:Description/dc:rights/text()')
    },
    namespaces={
    'dc': 'http://purl.org/dc/elements/1.1/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
    )


class Catalogue(common.ResumptionOAIPMH):
    TAG_CATEGORIES = ['author', 'epoch', 'kind', 'genre']
    
    def __init__(self):
        super(Catalogue, self).__init__()

        # earliest change
        year_zero = datetime(1990, 1, 1, 0, 0, 0)

        try:
            earliest_change = \
                Book.objects.order_by('changed_at')[0].changed_at
        except: earliest_change = year_zero

        try:
            earliest_delete = \
                Deleted.objects.ordery_by('deleted_at')[0].deleted_at
        except: earliest_delete = year_zero

        self.earliest_datestamp = earliest_change <= earliest_delete and \
            earliest_change or earliest_delete

        # admins
        self.admin_emails = [u.email for u in User.objects.filter(is_superuser=True)]

    def metadata(self, book):
        xml = etree.parse(book.xml_file)
        md = wl_dc_reader(xml)
        return md.getMap()

    def record_for_book(self, book, headers_only=False):
        meta = None
        identifier = str(WLURI.from_slug(book.slug))
        if isinstance(book, Book):
            setSpec = map(self.tag_to_setspec, book.tags.filter(category__in=self.TAG_CATEGORIES))
            header = common.Header(identifier, book.changed_at, setSpec, False)
            if not headers_only:
                meta = common.Metadata(self.metadata(book))
            about = None
        elif isinstance(book, Deleted):
            header = common.Header(identifier, book.deleted_at, [], True)
            if not headers_only:
                meta = common.Metadata({})
            about = None
        if headers_only:
            return header
        return header, meta, about

    def identify(self, **kw):
        ident = common.Identify(
            'Wolne Lektury',  # generate
            '%s/oaipmh' % WL_BASE,  # generate
            '2.0',  # version
            self.admin_emails,  # adminEmails
            self.earliest_datestamp,  # earliest datestamp of any change
            'persistent',  # deletedRecord
            'YYYY-MM-DDThh:mm:ssZ',  # granularity
            ['identity'],  # compression
            []  # descriptions
            )
        return ident

    def books(self, tag, from_, until):
        if tag:
            books = Book.tagged.with_all([tag])
        else:
            books = Book.objects.all()
        deleted = Deleted.objects.filter(slug__isnull=False)

        books = books.order_by('changed_at')
        deleted = deleted.order_by('deleted_at')
        if from_:
            books = books.filter(changed_at__gte=from_)
            deleted = deleted.filter(deleted_at__gte=from_)
            print "DELETED:%s" % deleted
        if until:
            books = books.filter(changed_at__lte=until)
            deleted = deleted.filter(deleted_at__lte=until)
        return list(books) + list(deleted)

    @staticmethod
    def tag_to_setspec(tag):
        return "%s:%s" % (tag.category, tag.slug)

    @staticmethod
    def setspec_to_tag(s):
        if not s: return None
        cs = s.split(':')
        if len(cs) == 2:
            if not cs[0] in Catalogue.TAG_CATEGORIES:
                raise error.NoSetHierarchyError()
            tag = Tag.objects.get(slug=cs[1], category=cs[0])
            return tag
        raise error.NoSetHierarchyError()

    def getRecord(self, **kw):
        """
Returns (header, metadata, about) for given record.
        """
        slug = WLURI(kw['identifier']).slug
        try:
            book = Book.objects.get(slug=slug)
            return self.record_for_book(book)
        except Book.DoesNotExist:
            book_type = ContentType.objects.get_for_model(Book)
            try:
                deleted_book = Deleted.objects.get(content_type=book_type,
                                                  slug=slug)
            except:
                raise error.NoRecordsMatchError()
            return self.record_for_book(deleted_book)

    def listIdentifiers(self, **kw):
        print "list identifiers %s" % (kw, )
        records = [self.record_for_book(book, headers_only=True) for
                   book in self.books(
                       self.setspec_to_tag(
                           kw.get('set', None)),
                           kw.get('from_', None),
                           kw.get('until', None))]
        return records, None

    def listRecords(self, **kw):
        """
can get a resumptionToken kw.
returns result, token
        """
        records = [self.record_for_book(book) for
                   book in self.books(
                       self.setspec_to_tag(
                           kw.get('set', None)),
                           kw.get('from_', None),
                           kw.get('until', None))]

        return records, None

    def listMetadataFormats(self, **kw):
        return [('oaidc',
                 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                 server.NS_OAIDC)]

    def listSets(self, **kw):
        tags = []
        for category in Catalogue.TAG_CATEGORIES:
            for tag in Tag.objects.filter(category=category):
                tags.append(("%s:%s" % (tag.category, tag.slug),
                             tag.name,
                             tag.description))
        return tags, None


