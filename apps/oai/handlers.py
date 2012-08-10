from oaipmh import server, common, metadata, error
from catalogue.models import Book, Tag
from api.models import Deleted
from api.handlers import WL_BASE
from librarian.dcparser import BookInfo
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from datetime import datetime
from lxml import etree
from lxml.etree import ElementTree
from django.db.models import Q
from django.conf import settings
from django.contrib.sites.models import Site


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
    
    def __init__(self, metadata_registry):
        super(Catalogue, self).__init__()
        self.metadata_registry = metadata_registry

        self.oai_id = "oai:"+Site.objects.get_current().domain+":%s"

        # earliest change
        year_zero = datetime(1990, 1, 1, 0, 0, 0)

        try:
            earliest_change = \
                Book.objects.order_by('changed_at')[0].changed_at
        except: earliest_change = year_zero

        try:
            earliest_delete = \
                Deleted.objects.exclude(slug__exact=u'').ordery_by('deleted_at')[0].deleted_at
        except: earliest_delete = year_zero

        self.earliest_datestamp = earliest_change <= earliest_delete and \
            earliest_change or earliest_delete

    def metadata(self, book):
        try:
            xml = etree.parse(book.xml_file)
        finally:
            book.xml_file.close()
        md = wl_dc_reader(xml)
        return md.getMap()

    def record_for_book(self, book, headers_only=False):
        meta = None
        identifier = self.slug_to_identifier(book.slug)
        if isinstance(book, Book):
            #            setSpec = map(self.tag_to_setspec, book.tags.filter(category__in=self.TAG_CATEGORIES))
            header = common.Header(identifier, book.changed_at, [], False)
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
            [m[1] for m in settings.MANAGERS],  # adminEmails
            self.earliest_datestamp,  # earliest datestamp of any change
            'persistent',  # deletedRecord
            'YYYY-MM-DDThh:mm:ssZ',  # granularity
            ['identity'],  # compression
            []  # descriptions
            )
        return ident

    def books(self, tag, from_, until):
        if tag:
            # we do not support sets, since they are problematic for deleted books.
            raise errror.NoSetHierarchyError("Wolne Lektury does not support sets.")
            # books = Book.tagged.with_all([tag])
        else:
            books = Book.objects.all()
        deleted = Deleted.objects.exclude(slug__exact=u'')

        books = books.order_by('changed_at')
        deleted = deleted.order_by('deleted_at')
        if from_:
            books = books.filter(changed_at__gte=from_)
            deleted = deleted.filter(deleted_at__gte=from_)
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
                raise error.NoSetHierarchyError("No category part in set")
            tag = Tag.objects.get(slug=cs[1], category=cs[0])
            return tag
        raise error.NoSetHierarchyError("Setspec should have two components: category:slug")

    def getRecord(self, **kw):
        """
Returns (header, metadata, about) for given record.
        """
        slug = self.identifier_to_slug(kw['identifier'])
        try:
            book = Book.objects.get(slug=slug)
            return self.record_for_book(book)
        except Book.DoesNotExist:
            book_type = ContentType.objects.get_for_model(Book)
            try:
                deleted_book = Deleted.objects.get(content_type=book_type,
                                                  slug=slug)
            except:
                raise error.IdDoesNotExistError("No item for this identifier")
            return self.record_for_book(deleted_book)

    def validate_kw(self, kw):
        if 'resumptionToken' in kw:
            raise error.BadResumptionTokenError("No resumption token support at this point")
        if 'metadataPrefix' in kw and not self.metadata_registry.hasWriter(kw['metadataPrefix']):
            raise error.CannotDisseminateFormatError("This format is not supported")

    def identifier_to_slug(self, ident):
        return ident.split(':')[-1]

    def slug_to_identifier(self, slug):
        return self.oai_id % slug

    def listIdentifiers(self, **kw):
        self.validate_kw(kw)
        records = [self.record_for_book(book, headers_only=True) for
                   book in self.books(None,
                           kw.get('from_', None),
                           kw.get('until', None))]
        return records, None

    def listRecords(self, **kw):
        """
can get a resumptionToken kw.
returns result, token
        """
        self.validate_kw(kw)
        records = [self.record_for_book(book) for
                   book in self.books(None,
                           kw.get('from_', None),
                           kw.get('until', None))]

        return records, None

    def listMetadataFormats(self, **kw):
        formats = [('oai_dc',
                 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                 server.NS_OAIDC)]
        if 'identifier' in kw:
            slug = self.identifier_to_slug(kw['identifier'])
            try:
                b = Book.objects.get(slug=slug)
                return formats
            except:
                try:
                    d = Deleted.objects.get(slug=slug)
                    return []
                except:
                    raise error.IdDoesNotExistError("This id does not exist")
        else:
            return formats

    def listSets(self, **kw):
        raise error.NoSetHierarchyError("Wolne Lektury does not support sets.")
        # tags = []
        # for category in Catalogue.TAG_CATEGORIES:
        #     for tag in Tag.objects.filter(category=category):
        #         tags.append(("%s:%s" % (tag.category, tag.slug),
        #                      tag.name,
        #                      tag.description))
        # return tags, None


