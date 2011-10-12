
from django.conf import settings
from lucene import SimpleFSDirectory, IndexWriter, File, Field, NumericField, PolishAnalyzer, \
    Version, Document, JavaError, IndexSearcher, QueryParser, Term
import os
import errno
from librarian import dcparser
from catalogue.models import Book


class IndexStore(object):
    def __init__(self):
        self.make_index_dir()
        self.store = SimpleFSDirectory(File(settings.SEARCH_INDEX))

    def make_index_dir(self):
        try:
            os.makedirs(settings.SEARCH_INDEX)
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else: raise


class Index(IndexStore):
    def __init__(self):
        IndexStore.__init__(self)
        self.index = None

    def open(self, analyzer=None):
        if not analyzer:
            analyzer = PolishAnalyzer(Version.LUCENE_34)
        if self.index:
            raise Exception("Index is already opened")
        self.index = IndexWriter(self.store, analyzer, IndexWriter.MaxFieldLength.LIMITED)
        return self.index

    def close(self):
        self.index.optimize()
        self.index.close()

    def index_book(self, book, overwrite=True):
        book_info = dcparser.parse(book.xml_file)

        if overwrite:
            self.index.deleteDocuments(Term("id", str(book.id)))

        doc = Document()
        doc.add(NumericField("id", Field.Store.YES, True).setIntValue(book.id))
        doc.add(Field("slug", book.slug, Field.Store.NO, Field.Index.ANALYZED_NO_NORMS))

        # validator, name
        for field in dcparser.BookInfo.FIELDS:
            if hasattr(book_info, field.name):
                if not getattr(book_info, field.name):
                    continue
                # since no type information is available, we use validator
                type_indicator = field.validator
                if type_indicator == dcparser.as_unicode:
                    s = getattr(book_info, field.name)
                    if field.multiple:
                        s = ', '.join(s)
                    try:
                        doc.add(Field(field.name, s, Field.Store.NO, Field.Index.ANALYZED))
                    except JavaError as je:
                        raise Exception("failed to add field: %s = '%s', %s(%s)" % (field.name, s, je.message, je.args))
                elif type_indicator == dcparser.as_person:
                    p = getattr(book_info, field.name)
                    if isinstance(p, dcparser.Person):
                        persons = str(p)
                    else:
                        persons = ', '.join(map(str, p))
                    doc.add(Field(field.name, persons, Field.Store.NO, Field.Index.ANALYZED))
                elif type_indicator == dcparser.as_date:
                    dt = getattr(book_info, field.name)
                    doc.add(Field(field.name, "%04d%02d%02d" % (dt.year, dt.month, dt.day), Field.Store.NO, Field.Index.NOT_ANALYZED))

        self.index.addDocument(doc)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.close()


class Search(IndexStore):
    def __init__(self, default_field="description"):
        IndexStore.__init__(self)
        self.analyzer = PolishAnalyzer(Version.LUCENE_34)
        self.searcher = IndexSearcher(self.store, True)
        self.parser = QueryParser(Version.LUCENE_34, default_field, self.analyzer)

    def query(self, query):
        return self.parser.parse(query)

    def search(self, query, max_results=50):
        """Returns (books, total_hits)
        """

        tops = self.searcher.search(self.query(query), max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(Book.objects.get(id=doc.get("id")))
        return (bks, tops.totalHits)
