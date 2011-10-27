# -*- coding: utf-8 -*-
from django.conf import settings
from lucene import SimpleFSDirectory, IndexWriter, File, Field, \
    NumericField, Version, Document, JavaError, IndexSearcher, \
    QueryParser, Term, PerFieldAnalyzerWrapper, \
    SimpleAnalyzer, PolishAnalyzer, ArrayList, \
    KeywordAnalyzer, NumericRangeQuery, BooleanQuery, \
    BlockJoinQuery, BlockJoinCollector, TermsFilter, \
    HashSet, BooleanClause, Term, CharTermAttribute, \
    PhraseQuery, StringReader
    # KeywordAnalyzer
import sys
import os
import errno
from librarian import dcparser
from librarian.parser import WLDocument
import catalogue.models
from multiprocessing.pool import ThreadPool
import atexit


class WLAnalyzer(PerFieldAnalyzerWrapper):
    def __init__(self):
        polish = PolishAnalyzer(Version.LUCENE_34)
        simple = SimpleAnalyzer(Version.LUCENE_34)
        keyword = KeywordAnalyzer(Version.LUCENE_34)
        # not sure if needed: there's NOT_ANALYZED meaning basically the same

        PerFieldAnalyzerWrapper.__init__(self, polish)

        self.addAnalyzer("tags", simple)
        self.addAnalyzer("technical_editors", simple)
        self.addAnalyzer("editors", simple)
        self.addAnalyzer("url", keyword)
        self.addAnalyzer("source_url", keyword)
        self.addAnalyzer("source_name", simple)
        self.addAnalyzer("publisher", simple)
        self.addAnalyzer("author", simple)
        self.addAnalyzer("is_book", keyword)

        #self.addanalyzer("fragment_anchor", keyword)


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
    def __init__(self, analyzer=None):
        IndexStore.__init__(self)
        self.index = None
        if not analyzer:
            analyzer = WLAnalyzer()
        self.analyzer = analyzer

    def open(self, analyzer=None):
        if self.index:
            raise Exception("Index is already opened")
        self.index = IndexWriter(self.store, self.analyzer,\
                                 IndexWriter.MaxFieldLength.LIMITED)
        return self.index

    def close(self):
        self.index.optimize()
        self.index.close()
        self.index = None

    def remove_book(self, book):
        q = NumericRangeQuery.newIntRange("book_id", book.id, book.id, True,True)
        self.index.deleteDocuments(q)

    def index_book(self, book, overwrite=True):
        if overwrite:
            self.remove_book(book)

        doc = self.extract_metadata(book)
        parts = self.extract_content(book)
        block = ArrayList().of_(Document)

        for p in parts:
            block.add(p)
        block.add(doc)
        self.index.addDocuments(block)

    master_tags = [
        'opowiadanie',
        'powiesc',
        'dramat_wierszowany_l',
        'dramat_wierszowany_lp',
        'dramat_wspolczesny', 'liryka_l', 'liryka_lp',
        'wywiad'
        ]

    skip_header_tags = ['autor_utworu', 'nazwa_utworu']

    def create_book_doc(self, book):
        """
        Create a lucene document connected to the book
        """
        doc = Document()
        doc.add(NumericField("book_id", Field.Store.YES, True).setIntValue(book.id))
        if book.parent is not None:
            doc.add(NumericField("parent_id", Field.Store.YES, True).setIntValue(book.parent.id))
        return doc

    def extract_metadata(self, book):
        book_info = dcparser.parse(book.xml_file)

        doc = self.create_book_doc(book)
        doc.add(Field("slug", book.slug, Field.Store.NO, Field.Index.ANALYZED_NO_NORMS))
        doc.add(Field("tags", ','.join([t.name for t in book.tags]), Field.Store.NO, Field.Index.ANALYZED))
        doc.add(Field("is_book", 'true', Field.Store.NO, Field.Index.NOT_ANALYZED))

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
                        persons = unicode(p)
                    else:
                        persons = ', '.join(map(unicode, p))
                    doc.add(Field(field.name, persons, Field.Store.NO, Field.Index.ANALYZED))
                elif type_indicator == dcparser.as_date:
                    dt = getattr(book_info, field.name)
                    doc.add(Field(field.name, "%04d%02d%02d" % (dt.year, dt.month, dt.day), Field.Store.NO, Field.Index.NOT_ANALYZED))
        return doc

    def get_master(self, root):
        for master in root.iter():
            if master.tag in self.master_tags:
                return master

    
    def extract_content(self, book):
        wld = WLDocument.from_file(book.xml_file.path)
        root = wld.edoc.getroot()

        # first we build a sequence of top-level items.
        # book_id
        # header_index - the 0-indexed position of header element.
        # content
        master = self.get_master(root)
        if master is None:
            return []
        
        header_docs = []
        for header, position in zip(list(master), range(len(master))):
            if header.tag in self.skip_header_tags:
                continue
            doc = self.create_book_doc(book)
            doc.add(NumericField("header_index", Field.Store.YES, True).setIntValue(position))
            doc.add(Field("header_type", header.tag, Field.Store.YES, Field.Index.NOT_ANALYZED))
            content = u' '.join([t for t in header.itertext()])
            doc.add(Field("content", content, Field.Store.NO, Field.Index.ANALYZED))
            header_docs.append(doc)

        def walker(node):
            yield node, None
            for child in list(node):
                for b, e in walker(child):
                    yield b, e
            yield None, node
            return

        # Then we create a document for each fragments
        # fragment_anchor - the anchor
        # themes - list of themes [not indexed]
        fragment_docs = []
        # will contain (framgent id -> { content: [], themes: [] }
        fragments = {}
        for start, end in walker(master):
            if start is not None and start.tag == 'begin':
                fid = start.attrib['id'][1:]
                fragments[fid] = {'content': [], 'themes': []}
                fragments[fid]['content'].append(start.tail)
            elif start is not None and start.tag == 'motyw':
                fid = start.attrib['id'][1:]
                fragments[fid]['themes'].append(start.text)
                fragments[fid]['content'].append(start.tail)
            elif start is not None and start.tag == 'end':
                fid = start.attrib['id'][1:]
                if fid not in fragments:
                    continue  # a broken <end> node, skip it
                frag = fragments[fid]
                del fragments[fid]

                def jstr(l):
                    return u' '.join(map(
                        lambda x: x == None and u'(none)' or unicode(x),
                        l))

                doc = self.create_book_doc(book)
                doc.add(Field("fragment_anchor", fid,
                              Field.Store.YES, Field.Index.NOT_ANALYZED))
                doc.add(Field("content",
                              u' '.join(filter(lambda s: s is not None, frag['content'])),
                              Field.Store.NO, Field.Index.ANALYZED))
                doc.add(Field("themes",
                              u' '.join(filter(lambda s: s is not None, frag['themes'])),
                              Field.Store.NO, Field.Index.ANALYZED))

                fragment_docs.append(doc)
            elif start is not None:
                for frag in fragments.values():
                    frag['content'].append(start.text)
            elif end is not None:
                for frag in fragments.values():
                    frag['content'].append(end.tail)

        return header_docs + fragment_docs

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.close()


class ReusableIndex(Index):
    """
    Works like index, but does not close/optimize Lucene index
    until program exit (uses atexit hook).
    This is usefull for importbooks command.

    if you cannot rely on atexit, use ReusableIndex.close_reusable() yourself.
    """
    index = None
    pool = None
    pool_jobs = None

    def open(self, analyzer=None, threads=4):
        if ReusableIndex.index is not None:
            self.index = ReusableIndex.index
        else:
            ReusableIndex.pool = ThreadPool(threads)
            ReusableIndex.pool_jobs = []
            Index.open(self, analyzer)
            ReusableIndex.index = self.index
            atexit.register(ReusableIndex.close_reusable)

    def index_book(self, *args, **kw):
        job = ReusableIndex.pool.apply_async(Index.index_book, args, kw)
        ReusableIndex.pool_jobs.append(job)

    @staticmethod
    def close_reusable():
        if ReusableIndex.index is not None:
            all_jobs = len(ReusableIndex.pool_jobs)
            waited=1
            for job in ReusableIndex.pool_jobs:
                sys.stdout.write("\rWaiting for search index job: %d/%d..." % 
                job.wait()
                waited+=1
            print("Indexing done.")
            ReusableIndex.pool.close()

            ReusableIndex.index.optimize()
            ReusableIndex.index.close()
            ReusableIndex.index = None

    def close(self):
        pass


class Search(IndexStore):
    def __init__(self, default_field="content"):
        IndexStore.__init__(self)
        self.analyzer = PolishAnalyzer(Version.LUCENE_34)
        ## self.analyzer = WLAnalyzer()
        self.searcher = IndexSearcher(self.store, True)
        self.parser = QueryParser(Version.LUCENE_34, default_field,
                                  self.analyzer)

        self.parent_filter = TermsFilter()
        self.parent_filter.addTerm(Term("is_book", "true"))

    def query(self, query):
        return self.parser.parse(query)

    def wrapjoins(self, query, fields=[]):
        """
        This functions modifies the query in a recursive way,
        so Term and Phrase Queries contained, which match
        provided fields are wrapped in a BlockJoinQuery,
        and so delegated to children documents.
        """
        if BooleanQuery.instance_(query):
            qs = BooleanQuery.cast_(query)
            for clause in qs:
                clause = BooleanClause.cast_(clause)
                clause.setQuery(self.wrapjoins(clause.getQuery(), fields))
            return qs
        else:
            termset = HashSet()
            query.extractTerms(termset)
            for t in termset:
                t = Term.cast_(t)
                if t.field() not in fields:
                    return query
            return BlockJoinQuery(query, self.parent_filter,
                                  BlockJoinQuery.ScoreMode.Total)

    def simple_search(self, query, max_results=50):
        """Returns (books, total_hits)
        """

        tops = self.searcher.search(self.query(query), max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(catalogue.models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

    def search(self, query, max_results=50):
        query = self.query(query)
        query = self.wrapjoins(query, ["content", "themes"])

        tops = self.searcher.search(query, max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(catalogue.models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

    def bsearch(self, query, max_results=50):
        q = self.query(query)
        bjq = BlockJoinQuery(q, self.parent_filter, BlockJoinQuery.ScoreMode.Avg)

        tops = self.searcher.search(bjq, max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(catalogue.models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

# TokenStream tokenStream = analyzer.tokenStream(fieldName, reader);
# OffsetAttribute offsetAttribute = tokenStream.getAttribute(OffsetAttribute.class);
# CharTermAttribute charTermAttribute = tokenStream.getAttribute(CharTermAttribute.class);

# while (tokenStream.incrementToken()) {
#     int startOffset = offsetAttribute.startOffset();
#     int endOffset = offsetAttribute.endOffset();
#     String term = charTermAttribute.toString();
# }


class MultiSearch(Search):
    """Class capable of IMDb-like searching"""
    def get_tokens(self, queryreader):
        if isinstance(queryreader, str):
            queryreader = StringReader(queryreader)
        queryreader.reset()
        tokens = self.analyzer.reusableTokenStream('content', queryreader)
        toks = []
        while tokens.incrementToken():
            cta = tokens.getAttribute(CharTermAttribute.class_)
            toks.append(cta)
        return toks

    def make_phrase(self, tokens, field='content', joined=False):
        phrase = PhraseQuery()
        for t in tokens:
            term = Term(field, t)
            phrase.add(term)
        if joined:
            phrase = self.content_query(phrase)
        return phrase

    def make_term_query(self, tokens, field='content', modal=BooleanClause.Occur.SHOULD, joined=False):
        q = BooleanQuery()
        for t in tokens:
            term = Term(field, t)
            q.add(BooleanClause(term, modal))
        if joined:
            self.content_query(q)
        return q

    def content_query(self, query):
        return BlockJoinQuery(query, self.parent_filter,
                              BlockJoinQuery.ScoreMode.Total)

    def multiseach(self, query, max_results=50):
        """
        Search strategy:
        - (phrase) OR -> content
                      -> title
                      -> author
        - (keywords)  -> author
                      -> motyw
                      -> tags
                      -> content
        """
        queryreader = StringReader(query)
        tokens = self.get_tokens(queryreader)

        top_level = BooleanQuery()
        Should = BooleanClause.Occur.SHOULD

        phrase_level = BooleanQuery()

        p_content = self.make_phrase(tokens, joined=True)
        p_title = self.make_phrase(tokens, 'title')
        p_author = self.make_phrase(tokens, 'author')

        phrase_level.add(BooleanClause(p_content, Should))
        phrase_level.add(BooleanClause(p_title, Should))
        phrase_level.add(BooleanClause(p_author, Should))

        kw_level = BooleanQuery()

        kw_level.add(self.make_term_query(tokens, 'author'), Should)
        kw_level.add(self.make_term_query(tokens, 'themes', joined=True), Should)
        kw_level.add(self.make_term_query(tokens, 'tags'), Should)
        kw_level.add(self.make_term_query(tokens, joined=True), Should)

        top_level.add(BooleanClause(phrase_level, Should))
        top_level.add(BooleanClause(kw_level, Should))

        tops = self.searcher.search(top_level, max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(catalogue.models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)
