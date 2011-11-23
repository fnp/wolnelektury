# -*- coding: utf-8 -*-

from django.conf import settings
from lucene import SimpleFSDirectory, IndexWriter, CheckIndex, \
    File, Field, Integer, \
    NumericField, Version, Document, JavaError, IndexSearcher, \
    QueryParser, PerFieldAnalyzerWrapper, \
    SimpleAnalyzer, PolishAnalyzer, ArrayList, \
    KeywordAnalyzer, NumericRangeQuery, BooleanQuery, \
    BlockJoinQuery, BlockJoinCollector, TermsFilter, \
    HashSet, BooleanClause, Term, CharTermAttribute, \
    PhraseQuery, MultiPhraseQuery, StringReader, TermQuery, BlockJoinQuery, \
    FuzzyQuery, FuzzyTermEnum, PrefixTermEnum, Sort, Integer, \
    SimpleHTMLFormatter, Highlighter, QueryScorer, TokenSources, TextFragment, \
    BooleanFilter, TermsFilter, FilterClause, QueryWrapperFilter, \
    initVM, CLASSPATH, JArray, JavaError
    # KeywordAnalyzer

# Initialize jvm
JVM = initVM(CLASSPATH)

import sys
import os
import re
import errno
from librarian import dcparser
from librarian.parser import WLDocument
from catalogue import models
from multiprocessing.pool import ThreadPool
from threading import current_thread
import atexit
import traceback


class WLAnalyzer(PerFieldAnalyzerWrapper):
    def __init__(self):
        polish = PolishAnalyzer(Version.LUCENE_34)
        polish_gap = PolishAnalyzer(Version.LUCENE_34)
        #        polish_gap.setPositionIncrementGap(999)

        simple = SimpleAnalyzer(Version.LUCENE_34)
        simple_gap = SimpleAnalyzer(Version.LUCENE_34)
        #        simple_gap.setPositionIncrementGap(999)

        keyword = KeywordAnalyzer(Version.LUCENE_34)

        # not sure if needed: there's NOT_ANALYZED meaning basically the same

        PerFieldAnalyzerWrapper.__init__(self, polish)

        self.addAnalyzer("tags", simple_gap)
        self.addAnalyzer("technical_editors", simple)
        self.addAnalyzer("editors", simple)
        self.addAnalyzer("url", keyword)
        self.addAnalyzer("source_url", keyword)
        self.addAnalyzer("source_name", simple)
        self.addAnalyzer("publisher", simple)
        self.addAnalyzer("author", simple)
        self.addAnalyzer("is_book", keyword)

        self.addAnalyzer("themes", simple_gap)
        self.addAnalyzer("themes_pl", polish_gap)

        self.addAnalyzer("tag_name", simple_gap)
        self.addAnalyzer("tag_name_pl", polish_gap)

        self.addAnalyzer("KEYWORD", keyword)
        self.addAnalyzer("SIMPLE", simple)
        self.addAnalyzer("POLISH", polish)


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


class IndexChecker(IndexStore):
    def __init__(self):
        IndexStore.__init__(self)

    def check(self):
        checker = CheckIndex(self.store)
        status = checker.checkIndex()
        return status


class Snippets(object):
    SNIPPET_DIR = "snippets"

    def __init__(self, book_id):
        try:
            os.makedirs(os.path.join(settings.SEARCH_INDEX, self.SNIPPET_DIR))
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else: raise
        self.book_id = book_id
        self.file = None

    def open(self, mode='r'):
        if not 'b' in mode:
            mode += 'b'
        self.file = open(os.path.join(settings.SEARCH_INDEX, self.SNIPPET_DIR, str(self.book_id)), mode)
        self.position = 0
        return self

    def add(self, snippet):
        l = len(snippet)
        self.file.write(snippet.encode('utf-8'))
        pos = (self.position, l)
        self.position += l
        return pos

    def get(self, pos):
        self.file.seek(pos[0], 0)
        return self.read(pos[1]).decode('utf-8')

    def close(self):
        self.file.close()


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

    def optimize(self):
        self.index.optimize()

    def close(self):
        try:
            self.index.optimize()
        except JavaError, je:
            print "Error during optimize phase, check index: %s" % je

        self.index.close()
        self.index = None

    def index_tags(self):
        q = NumericRangeQuery.newIntRange("tag_id", 0, Integer.MAX_VALUE, True, True)
        self.index.deleteDocuments(q)

        for tag in models.Tag.objects.all():
            doc = Document()
            doc.add(NumericField("tag_id", Field.Store.YES, True).setIntValue(tag.id))
            doc.add(Field("tag_name", tag.name, Field.Store.NO, Field.Index.ANALYZED))
            doc.add(Field("tag_name_pl", tag.name, Field.Store.NO, Field.Index.ANALYZED))
            doc.add(Field("tag_category", tag.category, Field.Store.NO, Field.Index.NOT_ANALYZED))
            self.index.addDocument(doc)

    def remove_book(self, book):
        q = NumericRangeQuery.newIntRange("book_id", book.id, book.id, True, True)
        self.index.deleteDocuments(q)

    def index_book(self, book, overwrite=True):
        if overwrite:
            self.remove_book(book)

        book_doc = self.create_book_doc(book)
        meta_fields = self.extract_metadata(book)
        for f in meta_fields.values():
            if isinstance(f, list):
                for elem in f:
                    book_doc.add(elem)
            else:
                book_doc.add(f)
                
        self.index.addDocument(book_doc)
        del book_doc

        self.index_content(book, book_fields=[meta_fields['title'], meta_fields['author']])

    master_tags = [
        'opowiadanie',
        'powiesc',
        'dramat_wierszowany_l',
        'dramat_wierszowany_lp',
        'dramat_wspolczesny', 'liryka_l', 'liryka_lp',
        'wywiad'
        ]

    skip_header_tags = ['autor_utworu', 'nazwa_utworu', 'dzielo_nadrzedne']

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
        fields = {}
        book_info = dcparser.parse(book.xml_file)

        print("extract metadata for book %s id=%d, thread%d" % (book.slug, book.id, current_thread().ident))

        fields['slug'] = Field("slug", book.slug, Field.Store.NO, Field.Index.ANALYZED_NO_NORMS)
        fields['tags'] = [Field("tags", t.name, Field.Store.NO, Field.Index.ANALYZED) for t in book.tags]
        fields['is_book'] = Field("is_book", 'true', Field.Store.NO, Field.Index.NOT_ANALYZED)

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
                        fields[field.name] = Field(field.name, s, Field.Store.NO, Field.Index.ANALYZED)
                    except JavaError as je:
                        raise Exception("failed to add field: %s = '%s', %s(%s)" % (field.name, s, je.message, je.args))
                elif type_indicator == dcparser.as_person:
                    p = getattr(book_info, field.name)
                    if isinstance(p, dcparser.Person):
                        persons = unicode(p)
                    else:
                        persons = ', '.join(map(unicode, p))
                    fields[field.name] = Field(field.name, persons, Field.Store.NO, Field.Index.ANALYZED)
                elif type_indicator == dcparser.as_date:
                    dt = getattr(book_info, field.name)
                    fields[field.name] = Field(field.name, "%04d%02d%02d" %\
                                               (dt.year, dt.month, dt.day), Field.Store.NO, Field.Index.NOT_ANALYZED)
        return fields

    def get_master(self, root):
        for master in root.iter():
            if master.tag in self.master_tags:
                return master

    def index_content(self, book, book_fields=[]):
        wld = WLDocument.from_file(book.xml_file.path)
        root = wld.edoc.getroot()

        master = self.get_master(root)
        if master is None:
            return []

        def walker(node):
            yield node, None
            for child in list(node):
                for b, e in walker(child):
                    yield b, e
            yield None, node
            return

        def fix_format(text):
            return re.sub("/$", "", text, flags=re.M)

        def add_part(snippets, **fields):
            doc = self.create_book_doc(book)
            for f in book_fields:
                doc.add(f)

            doc.add(NumericField('header_index', Field.Store.YES, True).setIntValue(fields["header_index"]))
            doc.add(NumericField("header_span", Field.Store.YES, True)\
                    .setIntValue('header_span' in fields and fields['header_span'] or 1))
            doc.add(Field('header_type', fields["header_type"], Field.Store.YES, Field.Index.NOT_ANALYZED))

            doc.add(Field('content', fields["content"], Field.Store.NO, Field.Index.ANALYZED, \
                          Field.TermVector.WITH_POSITIONS_OFFSETS))

            snip_pos = snippets.add(content)
            doc.add(NumericField("snippets_position", Field.Store.YES, True).setIntValue(snip_pos[0]))
            doc.add(NumericField("snippets_length", Field.Store.YES, True).setIntValue(snip_pos[1]))

            if 'fragment_anchor' in fields:
                doc.add(Field("fragment_anchor", fields['fragment_anchor'],
                              Field.Store.YES, Field.Index.NOT_ANALYZED))
                
            if 'themes' in fields:
                for theme in fields['themes']:
                    doc.add(Field("themes", theme, Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS))
                    doc.add(Field("themes_pl", theme, Field.Store.NO, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS))

            return doc

        fragments = {}
        snippets = Snippets(book.id).open('w')
        try:
            for header, position in zip(list(master), range(len(master))):

                if header.tag in self.skip_header_tags:
                    continue

                content = u' '.join([t for t in header.itertext()])
                content = fix_format(content)

                doc = add_part(snippets, header_index=position, header_type=header.tag, content=content)

                self.index.addDocument(doc)

                for start, end in walker(master):
                    if start is not None and start.tag == 'begin':
                        fid = start.attrib['id'][1:]
                        fragments[fid] = {'content': [], 'themes': [], 'start_section': position, 'start_header': header.tag}
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

                        doc = add_part(snippets,
                                       header_type=frag['start_header'],
                                       header_index=frag['start_section'],
                                       header_span=position - frag['start_section'] + 1,
                                       fragment_anchor=fid,
                                       content=u' '.join(filter(lambda s: s is not None, frag['content'])),
                                       themes=frag['themes'])

                        self.index.addDocument(doc)
                    elif start is not None:
                        for frag in fragments.values():
                            frag['content'].append(start.text)
                    elif end is not None:
                        for frag in fragments.values():
                            frag['content'].append(end.tail)
        finally:
            snippets.close()


    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.close()


def log_exception_wrapper(f):
    def _wrap(*a):
        try:
            f(*a)
        except Exception, e:
            print("Error in indexing thread: %s" % e)
            traceback.print_exc()
            raise e
    return _wrap


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
            print("opening index")
            ReusableIndex.pool = ThreadPool(threads, initializer=lambda: JVM.attachCurrentThread() )
            ReusableIndex.pool_jobs = []
            Index.open(self, analyzer)
            ReusableIndex.index = self.index
            atexit.register(ReusableIndex.close_reusable)

    def index_book(self, *args, **kw):
        job = ReusableIndex.pool.apply_async(log_exception_wrapper(Index.index_book), (self,) + args, kw)
        ReusableIndex.pool_jobs.append(job)

    @staticmethod
    def close_reusable():
        if ReusableIndex.index is not None:
            print("wait for indexing to finish")
            for job in ReusableIndex.pool_jobs:
                job.get()
                sys.stdout.write('.')
                sys.stdout.flush()
            print("done.")
            ReusableIndex.pool.close()

            ReusableIndex.index.optimize()
            ReusableIndex.index.close()
            ReusableIndex.index = None

    def close(self):
        pass


class Search(IndexStore):
    def __init__(self, default_field="content"):
        IndexStore.__init__(self)
        self.analyzer = WLAnalyzer() #PolishAnalyzer(Version.LUCENE_34)
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
            bks.append(models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

    def search(self, query, max_results=50):
        query = self.query(query)
        query = self.wrapjoins(query, ["content", "themes"])

        tops = self.searcher.search(query, max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

    def bsearch(self, query, max_results=50):
        q = self.query(query)
        bjq = BlockJoinQuery(q, self.parent_filter, BlockJoinQuery.ScoreMode.Avg)

        tops = self.searcher.search(bjq, max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

# TokenStream tokenStream = analyzer.tokenStream(fieldName, reader);
# OffsetAttribute offsetAttribute = tokenStream.getAttribute(OffsetAttribute.class);
# CharTermAttribute charTermAttribute = tokenStream.getAttribute(CharTermAttribute.class);

# while (tokenStream.incrementToken()) {
#     int startOffset = offsetAttribute.startOffset();
#     int endOffset = offsetAttribute.endOffset();
#     String term = charTermAttribute.toString();
# }


class SearchResult(object):
    def __init__(self, searcher, scoreDocs, score=None, how_found=None, snippets_cb=None):
        if score:
            self.score = score
        else:
            self.score = scoreDocs.score

        self.hits = []

        stored = searcher.doc(scoreDocs.doc)
        self.book_id = int(stored.get("book_id"))

        header_type = stored.get("header_type")
        sec = (header_type, int(stored.get("header_index")))
        header_span = stored.get('header_span')
        header_span = header_span is not None and int(header_span) or 1
        stored = searcher.doc(scoreDocs.doc)
        self.book_id = int(stored.get("book_id"))

        fragment = stored.get("fragment_anchor")

        hit = (sec + (header_span,), fragment, scoreDocs.score, {'how_found': how_found, 'snippets_cb': snippets_cb})

        self.hits.append(hit)

    def merge(self, other):
        if self.book_id != other.book_id:
            raise ValueError("this search result is or book %d; tried to merge with %d" % (self.book_id, other.book_id))
        self.hits += other.hits
        if other.score > self.score:
            self.score = other.score
        return self

    def add_snippets(self, snippets):
        self.snippets += snippets
        return self

    def get_book(self):
        return models.Book.objects.get(id=self.book_id)

    book = property(get_book)

    def get_parts(self):
        book = self.book

        def sections_covered(results):
            frags = filter(lambda r: r[1] is not None, results)
            sect = filter(lambda r: r[1] is None, results)
            sect = filter(lambda s: 0 == len(filter(
                lambda f: s[0][1] >= f[0][1] and s[0][1] < f[0][1] + f[0][2],
                frags)), sect)
            print "filtered, non overlapped sections: %s" % sect
            return frags + sect
            
            
        parts = [{"header": s[0], "position": s[1], '_score_key': s} for s in self.sections] \
            + [{"fragment": book.fragments.get(anchor=f), '_score_key':f} for f in self.fragments]

        parts.sort(lambda a, b: cmp(self.scores[a['_score_key']], self.scores[b['_score_key']]))
        print("bookid: %d parts: %s" % (self.book_id, parts))
        return parts

    parts = property(get_parts)


    def __unicode__(self):
        return u'SearchResult(book_id=%d, score=%d)' % (self.book_id, self.score)

    @staticmethod
    def aggregate(*result_lists):
        books = {}
        for rl in result_lists:
            for r in rl:
                if r.book_id in books:
                    books[r.book_id].merge(r)
                    #print(u"already have one with score %f, and this one has score %f" % (books[book.id][0], found.score))
                else:
                    books[r.book_id] = r
        return books.values()

    def __cmp__(self, other):
        return cmp(self.score, other.score)


class MultiSearch(Search):
    """Class capable of IMDb-like searching"""
    def get_tokens(self, searched, field='content'):
        """returns tokens analyzed by a proper (for a field) analyzer
        argument can be: StringReader, string/unicode, or tokens. In the last case
        they will just be returned (so we can reuse tokens, if we don't change the analyzer)
        """
        if isinstance(searched, str) or isinstance(searched, unicode):
            searched = StringReader(searched)
        elif isinstance(searched, list):
            return searched

        searched.reset()
        tokens = self.analyzer.reusableTokenStream(field, searched)
        toks = []
        while tokens.incrementToken():
            cta = tokens.getAttribute(CharTermAttribute.class_)
            toks.append(cta.toString())
        return toks

    def fuzziness(self, fuzzy):
        if not fuzzy:
            return None
        if isinstance(fuzzy, float) and fuzzy > 0.0 and fuzzy <= 1.0:
            return fuzzy
        else:
            return 0.5

    def make_phrase(self, tokens, field='content', slop=2, fuzzy=False):
        if fuzzy:
            phrase = MultiPhraseQuery()
            for t in tokens:
                term = Term(field, t)
                fuzzterm = FuzzyTermEnum(self.searcher.getIndexReader(), term, self.fuzziness(fuzzy))
                fuzzterms = []

                while True:
                    #                    print("fuzz %s" % unicode(fuzzterm.term()).encode('utf-8'))
                    ft = fuzzterm.term()
                    if ft:
                        fuzzterms.append(ft)
                    if not fuzzterm.next(): break
                if fuzzterms:
                    phrase.add(JArray('object')(fuzzterms, Term))
                else:
                    phrase.add(term)
        else:
            phrase = PhraseQuery()
            phrase.setSlop(slop)
            for t in tokens:
                term = Term(field, t)
                phrase.add(term)
        return phrase

    def make_term_query(self, tokens, field='content', modal=BooleanClause.Occur.SHOULD, fuzzy=False):
        q = BooleanQuery()
        for t in tokens:
            term = Term(field, t)
            if fuzzy:
                term = FuzzyQuery(term, self.fuzziness(fuzzy))
            else:
                term = TermQuery(term)
            q.add(BooleanClause(term, modal))
        return q

    def content_query(self, query):
        return BlockJoinQuery(query, self.parent_filter,
                              BlockJoinQuery.ScoreMode.Total)

    def search_perfect_book(self, searched, max_results=20, fuzzy=False):
        qrys = [self.make_phrase(self.get_tokens(searched, field=fld), field=fld, fuzzy=fuzzy) for fld in ['author', 'title']]

        books = []
        for q in qrys:
            top = self.searcher.search(q, max_results)
            for found in top.scoreDocs:
                books.append(SearchResult(self.searcher, found))
        return books

    def search_perfect_parts(self, searched, max_results=20, fuzzy=False):
        qrys = [self.make_phrase(self.get_tokens(searched), field=fld, fuzzy=fuzzy) for fld in ['content']]

        books = []
        for q in qrys:
            top = self.searcher.search(q, max_results)
            for found in top.scoreDocs:
                books.append(SearchResult(self.searcher, found).add_snippets(self.get_snippets(found, q)))

        return books

    def search_everywhere(self, searched, max_results=20, fuzzy=False):
        books = []

        # content only query : themes x content
        q = BooleanQuery()

        tokens = self.get_tokens(searched)
        q.add(BooleanClause(self.make_term_query(tokens, field='themes', fuzzy=fuzzy), BooleanClause.Occur.MUST))
        q.add(BooleanClause(self.make_term_query(tokens, field='content', fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

        topDocs = self.searcher.search(q, max_results)
        for found in topDocs.scoreDocs:
            books.append(SearchResult(self.searcher, found))

        # joined query themes/content x author/title/epochs/genres/kinds
        # q = BooleanQuery()
        # in_meta = BooleanQuery()
        # in_content = BooleanQuery()

        # for fld in ['themes', 'content']:
        #     in_content.add(BooleanClause(self.make_term_query(tokens, field=fld, fuzzy=False), BooleanClause.Occur.SHOULD))

        # in_meta.add(BooleanClause(self.make_term_query(
        #     self.get_tokens(searched, field='author'), field='author', fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

        # for fld in ['title', 'epochs', 'genres', 'kinds']:
        #     in_meta.add(BooleanClause(self.make_term_query(tokens, field=fld, fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

        # q.add(BooleanClause(in_meta, BooleanClause.Occur.MUST))
        # in_content_join = self.content_query(in_content)
        # q.add(BooleanClause(in_content_join, BooleanClause.Occur.MUST))
        # #        import pdb; pdb.set_trace()
        # collector = BlockJoinCollector(Sort.RELEVANCE, 100, True, True)

        # self.searcher.search(q, collector)

        # top_groups = collector.getTopGroups(in_content_join, Sort.RELEVANCE, 0, max_results, 0, True)
        # if top_groups:
        #     for grp in top_groups.groups:
        #         for part in grp.scoreDocs:
        #             books.append(SearchResult(self.searcher, part, score=grp.maxScore))
        return books

    def multisearch(self, query, max_results=50):
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
        # queryreader = StringReader(query)
        # tokens = self.get_tokens(queryreader)

        # top_level = BooleanQuery()
        # Should = BooleanClause.Occur.SHOULD

        # phrase_level = BooleanQuery()
        # phrase_level.setBoost(1.3)

        # p_content = self.make_phrase(tokens, joined=True)
        # p_title = self.make_phrase(tokens, 'title')
        # p_author = self.make_phrase(tokens, 'author')

        # phrase_level.add(BooleanClause(p_content, Should))
        # phrase_level.add(BooleanClause(p_title, Should))
        # phrase_level.add(BooleanClause(p_author, Should))

        # kw_level = BooleanQuery()

        # kw_level.add(self.make_term_query(tokens, 'author'), Should)
        # j_themes = self.make_term_query(tokens, 'themes', joined=True)
        # kw_level.add(j_themes, Should)
        # kw_level.add(self.make_term_query(tokens, 'tags'), Should)
        # j_con = self.make_term_query(tokens, joined=True)
        # kw_level.add(j_con, Should)

        # top_level.add(BooleanClause(phrase_level, Should))
        # top_level.add(BooleanClause(kw_level, Should))

        return None

    def book_search(self, query, filter=None, max_results=50, collector=None):
        tops = self.searcher.search(query, filter, max_results)
        #tops = self.searcher.search(p_content, max_results)

        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            b = models.Book.objects.get(id=doc.get("book_id"))
            bks.append(b)
            print "%s (%d) -> %f" % (b, b.id, found.score)
        return bks

    def get_snippets(self, scoreDoc, query, field='content'):
        htmlFormatter = SimpleHTMLFormatter()
        highlighter = Highlighter(htmlFormatter, QueryScorer(query))

        stored = self.searcher.doc(scoreDoc.doc)

        # locate content.
        snippets = Snippets(stored.get('book_id')).open()
        try:
            text = snippets.get(stored.get('snippets_position'), stored.get('snippets_length'))
        finally:
            snippets.close()

        tokenStream = TokenSources.getAnyTokenStream(self.searcher.getIndexReader(), scoreDoc.doc, field, self.analyzer)
        #  highlighter.getBestTextFragments(tokenStream, text, False, 10)
        snip = highlighter.getBestFragments(tokenStream, text, 3, "...")
        print('snips: %s' % snip)

        return [snip]

    @staticmethod
    def enum_to_array(enum):
        """
        Converts a lucene TermEnum to array of Terms, suitable for
        addition to queries
        """
        terms = []

        while True:
            t = enum.term()
            if t:
                terms.append(t)
            if not enum.next(): break

        if terms:
            return JArray('object')(terms, Term)

    def search_tags(self, query, filter=None, max_results=40):
        tops = self.searcher.search(query, filter, max_results)

        tags = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            tag = models.Tag.objects.get(id=doc.get("tag_id"))
            tags.append(tag)
            print "%s (%d) -> %f" % (tag, tag.id, found.score)

        return tags

    def create_prefix_phrase(self, toks, field):
        q = MultiPhraseQuery()
        for i in range(len(toks)):
            t = Term(field, toks[i])
            if i == len(toks) - 1:
                pterms = MultiSearch.enum_to_array(PrefixTermEnum(self.searcher.getIndexReader(), t))
                if pterms:
                    q.add(pterms)
                else:
                    q.add(t)
            else:
                q.add(t)
        return q

    def hint_tags(self, string, max_results=50):
        toks = self.get_tokens(string, field='SIMPLE')
        top = BooleanQuery()

        for field in ['tag_name', 'tag_name_pl']:
            q = self.create_prefix_phrase(toks, field)
            top.add(BooleanClause(q, BooleanClause.Occur.SHOULD))

        book_cat = TermsFilter()
        book_cat.addTerm(Term("tag_category", "book"))

        no_book_cat = BooleanFilter()
        no_book_cat.add(FilterClause(book_cat, BooleanClause.Occur.MUST_NOT))

        return self.search_tags(top, no_book_cat, max_results=max_results)

    def hint_books(self, string, max_results=50):
        toks = self.get_tokens(string, field='SIMPLE')

        q = self.create_prefix_phrase(toks, 'title')
        only_books = TermsFilter()
        only_books.addTerm(Term("is_book", "true"))

        return self.book_search(q, only_books, max_results=max_results)

    def filter_by_tags(self, tags):
        q = BooleanQuery()
        
        for tag in tags:
            toks = self.get_tokens(tag.name, field='tags')
            tag_phrase = PhraseQuery()
            for tok in toks:
                tag_phrase.add(tok)
            q.add(BooleanClause(tok, BooleanClause.Occur.MUST))

        return QueryWrapperFilter(q)

    def filtered_categories(self, tags):
        cats = {}
        for t in tags:
            cats[t.category] = True
        return cats.keys()
