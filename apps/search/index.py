# -*- coding: utf-8 -*-

from django.conf import settings

import os
import re
import errno
from librarian import dcparser
from librarian.parser import WLDocument
from lxml import etree
import catalogue.models
from pdcounter.models import Author as PDCounterAuthor, BookStub as PDCounterBook
from itertools import chain
import traceback
import logging
log = logging.getLogger('search')
import sunburnt
import highlight


class SolrIndex(object):
    def __init__(self, mode=None):
        self.index = highlight.HLSolrInterface(settings.SOLR, mode=mode)


class Snippets(object):
    """
    This class manages snippet files for indexed object (book)
    the snippets are concatenated together, and their positions and
    lengths are kept in lucene index fields.
    """
    SNIPPET_DIR = "snippets"

    def __init__(self, book_id, revision=None):
        try:
            os.makedirs(os.path.join(settings.SEARCH_INDEX, self.SNIPPET_DIR))
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else: raise
        self.book_id = book_id
        self.revision = revision
        self.file = None

    @property
    def path(self):
        if self.revision: fn = "%d.%d" % (self.book_id, self.revision)
        else: fn = "%d" % self.book_id

        return os.path.join(settings.SEARCH_INDEX, self.SNIPPET_DIR, fn)

    def open(self, mode='r'):
        """
        Open the snippet file. Call .close() afterwards.
        """
        if not 'b' in mode:
            mode += 'b'

        if 'w' in mode:
            if os.path.exists(self.path):
                self.revision = 1
                while True:
                    if not os.path.exists(self.path):
                        break
                    self.revision += 1

        self.file = open(self.path, mode)
        self.position = 0
        return self

    def add(self, snippet):
        """
        Append a snippet (unicode) to the snippet file.
        Return a (position, length) tuple
        """
        txt = snippet.encode('utf-8')
        l = len(txt)
        self.file.write(txt)
        pos = (self.position, l)
        self.position += l
        return pos

    def get(self, pos):
        """
        Given a tuple of (position, length) return an unicode
        of the snippet stored there.
        """
        self.file.seek(pos[0], 0)
        txt = self.file.read(pos[1]).decode('utf-8')
        return txt

    def close(self):
        """Close snippet file"""
        self.file.close()

    def remove(self):
        self.revision = None
        try:
            os.unlink(self.path)
            self.revision = 0
            while True:
                self.revision += 1
                os.unlink(self.path)
        except OSError:
            pass


class Index(SolrIndex):
    """
    Class indexing books.
    """
    def __init__(self):
        super(Index, self).__init__()

    def delete_query(self, *queries):
        """
        index.delete(queries=...) doesn't work, so let's reimplement it
        using deletion of list of uids.
        """
        uids = set()
        for q in queries:
            if isinstance(q, sunburnt.search.LuceneQuery):
                q = self.index.query(q)
            q.field_limiter.update(['uid'])
            st = 0
            rows = 100
            while True:
                ids = q.paginate(start=st, rows=rows).execute()
                if not len(ids):
                    break
                for res in ids:
                    uids.add(res['uid'])
                st+=rows
                #        print "Will delete %s" % ','.join([x for x in uids])
        if uids:
            self.index.delete(uids)
            return True
        else:
            return False

    def index_tags(self, *tags, **kw):
        """
        Re-index global tag list.
        Removes all tags from index, then index them again.
        Indexed fields include: id, name (with and without polish stems), category
        """
        remove_only = kw.get('remove_only', False)
        # first, remove tags from index.
        if tags:
            tag_qs = []
            for tag in tags:
                q_id = self.index.Q(tag_id=tag.id)

                if isinstance(tag, PDCounterAuthor):
                    q_cat = self.index.Q(tag_category='pd_author')
                elif isinstance(tag, PDCounterBook):
                    q_cat = self.index.Q(tag_category='pd_book')
                else:
                    q_cat = self.index.Q(tag_category=tag.category)

                q_id_cat = self.index.Q(q_id & q_cat)
                tag_qs.append(q_id_cat)
            self.delete_query(tag_qs)
        else:  # all
            q = self.index.Q(tag_id__any=True)
            self.delete_query(q)

        if not remove_only:
            # then add them [all or just one passed]
            if not tags:
                tags = chain(catalogue.models.Tag.objects.exclude(category='set'), \
                    PDCounterAuthor.objects.all(), \
                    PDCounterBook.objects.all())

            for tag in tags:
                if isinstance(tag, PDCounterAuthor):
                    doc = {
                        "tag_id": int(tag.id),
                        "tag_name": tag.name,
                        "tag_name_pl": tag.name,
                        "tag_category": 'pd_author',
                        "is_pdcounter": True
                        }
                elif isinstance(tag, PDCounterBook):
                    doc = {
                        "tag_id": int(tag.id),
                        "tag_name": tag.title,
                        "tag_name_pl": tag.title,
                        "tag_category": 'pd_book',
                        "is_pdcounter": True
                        }
                else:
                    doc = {
                        "tag_id": int(tag.id),
                        "tag_name": tag.name,
                        "tag_name_pl": tag.name,
                        "tag_category": tag.category,
                        "is_pdcounter": False
                        }
                doc['uid'] = "tag%d" % tag.id
                self.index.add(doc)

    def create_book_doc(self, book):
        """
        Create a lucene document referring book id.
        """
        doc = {
            'book_id': int(book.id),
            }
        if book.parent is not None:
            doc["parent_id"] = int(book.parent.id)
        return doc

    def remove_book(self, book_or_id, remove_snippets=True):
        """Removes a book from search index.
        book - Book instance."""
        if isinstance(book_or_id, catalogue.models.Book):
            book_id = book_or_id.id
        else:
            book_id = book_or_id

        self.delete_query(self.index.Q(book_id=book_id))

        if remove_snippets:
            snippets = Snippets(book_id)
            snippets.remove()

    def index_book(self, book, book_info=None, overwrite=True):
        """
        Indexes the book.
        Creates a lucene document for extracted metadata
        and calls self.index_content() to index the contents of the book.
        """
        if overwrite:
            # we don't remove snippets, since they might be still needed by
            # threads using not reopened index
            self.remove_book(book, remove_snippets=False)

        book_doc = self.create_book_doc(book)
        meta_fields = self.extract_metadata(book, book_info, dc_only=['source_name', 'authors', 'title'])
        # let's not index it - it's only used for extracting publish date
        if 'source_name' in meta_fields:
            del meta_fields['source_name']

        for n, f in meta_fields.items():
            book_doc[n] = f

        book_doc['uid'] = "book%s" % book_doc['book_id']
        self.index.add(book_doc)
        del book_doc

        self.index_content(book, book_fields={
            'title': meta_fields['title'],
            'authors': meta_fields['authors'],
            'published_date': meta_fields['published_date']})

    master_tags = [
        'opowiadanie',
        'powiesc',
        'dramat_wierszowany_l',
        'dramat_wierszowany_lp',
        'dramat_wspolczesny', 'liryka_l', 'liryka_lp',
        'wywiad',
        ]

    ignore_content_tags = [
        'uwaga', 'extra',
        'zastepnik_tekstu', 'sekcja_asterysk', 'separator_linia', 'zastepnik_wersu',
        'didaskalia',
        'naglowek_aktu', 'naglowek_sceny', 'naglowek_czesc',
        ]

    footnote_tags = ['pa', 'pt', 'pr', 'pe']

    skip_header_tags = ['autor_utworu', 'nazwa_utworu', 'dzielo_nadrzedne', '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF']

    published_date_re = re.compile("([0-9]+)[\]. ]*$")

    def extract_metadata(self, book, book_info=None, dc_only=None):
        """
        Extract metadata from book and returns a map of fields keyed by fieldname
        """
        fields = {}

        if book_info is None:
            book_info = dcparser.parse(open(book.xml_file.path))

        fields['slug'] = book.slug
        fields['tags'] = [t.name  for t in book.tags]
        fields['is_book'] = True

        # validator, name
        for field in dcparser.BookInfo.FIELDS:
            if dc_only and field.name not in dc_only:
                continue
            if hasattr(book_info, field.name):
                if not getattr(book_info, field.name):
                    continue
                # since no type information is available, we use validator
                type_indicator = field.validator
                if type_indicator == dcparser.as_unicode:
                    s = getattr(book_info, field.name)
                    if field.multiple:
                        s = ', '.join(s)
                    fields[field.name] = s
                elif type_indicator == dcparser.as_person:
                    p = getattr(book_info, field.name)
                    if isinstance(p, dcparser.Person):
                        persons = unicode(p)
                    else:
                        persons = ', '.join(map(unicode, p))
                    fields[field.name] = persons
                elif type_indicator == dcparser.as_date:
                    dt = getattr(book_info, field.name)
                    fields[field.name] = dt

        # get published date
        pd = None
        if hasattr(book_info, 'source_name') and book_info.source_name:
            match = self.published_date_re.search(book_info.source_name)
            if match is not None:
                pd = str(match.groups()[0])
        if not pd: pd = ""
        fields["published_date"] = pd

        return fields

    # def add_gaps(self, fields, fieldname):
    #     """
    #     Interposes a list of fields with gap-fields, which are indexed spaces and returns it.
    #     This allows for doing phrase queries which do not overlap the gaps (when slop is 0).
    #     """
    #     def gap():
    #         while True:
    #             yield Field(fieldname, ' ', Field.Store.NO, Field.Index.NOT_ANALYZED)
    #     return reduce(lambda a, b: a + b, zip(fields, gap()))[0:-1]

    def get_master(self, root):
        """
        Returns the first master tag from an etree.
        """
        for master in root.iter():
            if master.tag in self.master_tags:
                return master

    def index_content(self, book, book_fields={}):
        """
        Walks the book XML and extract content from it.
        Adds parts for each header tag and for each fragment.
        """
        wld = WLDocument.from_file(book.xml_file.path, parse_dublincore=False)
        root = wld.edoc.getroot()

        master = self.get_master(root)
        if master is None:
            return []

        def walker(node, ignore_tags=[]):

            if node.tag not in ignore_tags:
                yield node, None, None
                if node.text is not None:
                    yield None, node.text, None
                for child in list(node):
                    for b, t, e in walker(child):
                        yield b, t, e
                yield None, None, node

            if node.tail is not None:
                yield None, node.tail, None
            return

        def fix_format(text):
            #            separator = [u" ", u"\t", u".", u";", u","]
            if isinstance(text, list):
                # need to join it first
                text = filter(lambda s: s is not None, content)
                text = u' '.join(text)
                # for i in range(len(text)):
                #     if i > 0:
                #         if text[i][0] not in separator\
                #             and text[i - 1][-1] not in separator:
                #          text.insert(i, u" ")

            return re.sub("(?m)/$", "", text)

        def add_part(snippets, **fields):
            doc = self.create_book_doc(book)
            for n, v in book_fields.items():
                doc[n] = v

            doc['header_index'] = fields["header_index"]
            doc['header_span'] = 'header_span' in fields and fields['header_span'] or 1
            doc['header_type'] = fields['header_type']

            doc['text'] = fields['text']

            # snippets
            snip_pos = snippets.add(fields["text"])

            doc['snippets_position'] = snip_pos[0]
            doc['snippets_length'] = snip_pos[1]
            if snippets.revision:
                doc["snippets_revision"] = snippets.revision

            if 'fragment_anchor' in fields:
                doc["fragment_anchor"] = fields['fragment_anchor']

            if 'themes' in fields:
                doc['themes'] = fields['themes']
            doc['uid'] = "part%s%s%s" % (doc['header_index'],
                                         doc['header_span'],
                                         doc.get('fragment_anchor',''))
            return doc

        def give_me_utf8(s):
            if isinstance(s, unicode):
                return s.encode('utf-8')
            else:
                return s

        fragments = {}
        snippets = Snippets(book.id).open('w')
        try:
            for header, position in zip(list(master), range(len(master))):

                if header.tag in self.skip_header_tags:
                    continue
                if header.tag is etree.Comment:
                    continue

                # section content
                content = []
                footnote = []

                def all_content(text):
                    for frag in fragments.values():
                        frag['text'].append(text)
                    content.append(text)
                handle_text = [all_content]

                for start, text, end in walker(header, ignore_tags=self.ignore_content_tags):
                    # handle footnotes
                    if start is not None and start.tag in self.footnote_tags:
                        footnote = []

                        def collect_footnote(t):
                            footnote.append(t)

                        handle_text.append(collect_footnote)
                    elif end is not None and footnote is not [] and end.tag in self.footnote_tags:
                        handle_text.pop()
                        doc = add_part(snippets, header_index=position, header_type=header.tag,
                                       text=u''.join(footnote),
                                       is_footnote=True)

                        self.index.add(doc)
                        #print "@ footnote text: %s" % footnote
                        footnote = []

                    # handle fragments and themes.
                    if start is not None and start.tag == 'begin':
                        fid = start.attrib['id'][1:]
                        fragments[fid] = {'text': [], 'themes': [], 'start_section': position, 'start_header': header.tag}

                    # themes for this fragment
                    elif start is not None and start.tag == 'motyw':
                        fid = start.attrib['id'][1:]
                        handle_text.append(None)
                        if start.text is not None:
                            fragments[fid]['themes'] += map(unicode.strip, map(unicode, (start.text.split(','))))
                    elif end is not None and end.tag == 'motyw':
                        handle_text.pop()

                    elif start is not None and start.tag == 'end':
                        fid = start.attrib['id'][1:]
                        if fid not in fragments:
                            continue  # a broken <end> node, skip it
                        frag = fragments[fid]
                        if frag['themes'] == []:
                            continue  # empty themes list.
                        del fragments[fid]

                        doc = add_part(snippets,
                                       header_type=frag['start_header'],
                                       header_index=frag['start_section'],
                                       header_span=position - frag['start_section'] + 1,
                                       fragment_anchor=fid,
                                       text=fix_format(frag['text']),
                                       themes=frag['themes'])
                        #print '@ FRAG %s' % frag['content']
                        self.index.add(doc)

                        # Collect content.

                    if text is not None and handle_text is not []:
                        hdl = handle_text[-1]
                        if hdl is not None:
                            hdl(text)

                        # in the end, add a section text.
                doc = add_part(snippets, header_index=position,
                               header_type=header.tag, text=fix_format(content))
                #print '@ CONTENT: %s' % fix_format(content)

                self.index.add(doc)

        finally:
            snippets.close()



class SearchResult(object):
    def __init__(self, search, doc, how_found=None, snippets=None, searched=None, tokens_cache=None):
        if tokens_cache is None: tokens_cache = {}

        if 'score' in doc:
            self._score = doc['score']
        else:
            self._score = 0

        self.boost = 1.0

        self._hits = []
        self._processed_hits = None  # processed hits

        self.book_id = int(doc["book_id"])

        pd = doc["published_date"]
        try:
            self.published_date = int(pd)
        except ValueError:
            self.published_date = 0

        header_type = doc.get("header_type", None)
        # we have a content hit in some header of fragment
        if header_type is not None:
            sec = (header_type, int(doc["header_index"]))
            header_span = doc['header_span']
            header_span = header_span is not None and int(header_span) or 1

            fragment = doc.get("fragment_anchor", None)

            if snippets:
                snippets = snippets.replace("/\n", "\n")
            hit = (sec + (header_span,), fragment, self._score, {'how_found': how_found, 'snippets': snippets and [snippets] or []})

            self._hits.append(hit)

        self.search = search
        self.searched = searched
        self.tokens_cache = tokens_cache

    @property
    def score(self):
        return self._score * self.boost

    def merge(self, other):
        if self.book_id != other.book_id:
            raise ValueError("this search result is or book %d; tried to merge with %d" % (self.book_id, other.book_id))
        self._hits += other._hits
        if other.score > self.score:
            self._score = other._score
        return self

    def get_book(self):
        if hasattr(self, '_book'):
            return self._book
        return catalogue.models.Book.objects.get(id=self.book_id)

    book = property(get_book)

    @property
    def hits(self):
        if self._processed_hits is not None:
            return self._processed_hits

        POSITION = 0
        FRAGMENT = 1
        POSITION_INDEX = 1
        POSITION_SPAN = 2
        SCORE = 2
        OTHER = 3

        # to sections and fragments
        frags = filter(lambda r: r[FRAGMENT] is not None, self._hits)

        sect = filter(lambda r: r[FRAGMENT] is None, self._hits)

        # sections not covered by fragments
        sect = filter(lambda s: 0 == len(filter(
            lambda f: s[POSITION][POSITION_INDEX] >= f[POSITION][POSITION_INDEX]
            and s[POSITION][POSITION_INDEX] < f[POSITION][POSITION_INDEX] + f[POSITION][POSITION_SPAN],
            frags)), sect)

        hits = []

        def remove_duplicates(lst, keyfn, compare):
            els = {}
            for e in lst:
                eif = keyfn(e)
                if eif in els:
                    if compare(els[eif], e) >= 1:
                        continue
                els[eif] = e
            return els.values()

        # remove fragments with duplicated fid's and duplicated snippets
        frags = remove_duplicates(frags, lambda f: f[FRAGMENT], lambda a, b: cmp(a[SCORE], b[SCORE]))
        frags = remove_duplicates(frags, lambda f: f[OTHER]['snippets'] and f[OTHER]['snippets'][0] or f[FRAGMENT],
                                  lambda a, b: cmp(a[SCORE], b[SCORE]))

        # remove duplicate sections
        sections = {}

        for s in sect:
            si = s[POSITION][POSITION_INDEX]
            # skip existing
            if si in sections:
                if sections[si]['score'] >= s[SCORE]:
                    continue

            m = {'score': s[SCORE],
                 'section_number': s[POSITION][POSITION_INDEX] + 1,
                 }
            m.update(s[OTHER])
            sections[si] = m

        hits = sections.values()

        for f in frags:
            try:
                frag = catalogue.models.Fragment.objects.get(anchor=f[FRAGMENT], book__id=self.book_id)
            except catalogue.models.Fragment.DoesNotExist:
                # stale index
                continue

            # Figure out if we were searching for a token matching some word in theme name.
            themes = frag.tags.filter(category='theme')
            themes_hit = []
            if self.searched is not None:
                tokens = self.search.get_tokens(self.searched, 'POLISH', cached=self.tokens_cache)
                for theme in themes:
                    name_tokens = self.search.get_tokens(theme.name, 'POLISH')
                    for t in tokens:
                        if t in name_tokens:
                            if not theme in themes_hit:
                                themes_hit.append(theme)
                            break

            m = {'score': f[SCORE],
                 'fragment': frag,
                 'section_number': f[POSITION][POSITION_INDEX] + 1,
                 'themes': themes,
                 'themes_hit': themes_hit
                 }
            m.update(f[OTHER])
            hits.append(m)

        hits.sort(lambda a, b: cmp(a['score'], b['score']), reverse=True)

        self._processed_hits = hits

        return hits

    def __unicode__(self):
        return u'SearchResult(book_id=%d, score=%d)' % (self.book_id, self.score)

    @staticmethod
    def aggregate(*result_lists):
        books = {}
        for rl in result_lists:
            for r in rl:
                if r.book_id in books:
                    books[r.book_id].merge(r)
                else:
                    books[r.book_id] = r
        return books.values()

    def __cmp__(self, other):
        c = cmp(self.score, other.score)
        if c == 0:
            # this is inverted, because earlier date is better
            return cmp(other.published_date, self.published_date)
        else:
            return c


class Hint(object):
    """
    Given some hint information (information we already know about)
    our search target - like author, title (specific book), epoch, genre, kind
    we can narrow down search using filters.
    """
    def __init__(self, search):
        """
        Accepts a Searcher instance.
        """
        self.search = search
        self.book_tags = {}
        self.part_tags = []
        self._books = []

    def books(self, *books):
        """
        Give a hint that we search these books.
        """
        self._books = books

    def tags(self, tags):
        """
        Give a hint that these Tag objects (a list of)
        is necessary.
        """
        for t in tags:
            if t.category in ['author', 'title', 'epoch', 'genre', 'kind']:
                lst = self.book_tags.get(t.category, [])
                lst.append(t)
                self.book_tags[t.category] = lst
            if t.category in ['theme', 'theme_pl']:
                self.part_tags.append(t)

    def tag_filter(self, tags, field='tags'):
        """
        Given a lsit of tags and an optional field (but they are normally in tags field)
        returns a filter accepting only books with specific tags.
        """
        q = BooleanQuery()

        for tag in tags:
            toks = self.search.get_tokens(tag.name, field=field)
            tag_phrase = PhraseQuery()
            for tok in toks:
                tag_phrase.add(Term(field, tok))
            q.add(BooleanClause(tag_phrase, BooleanClause.Occur.MUST))

        return QueryWrapperFilter(q)

    def book_filter(self):
        """
        Filters using book tags (all tag kinds except a theme)
        """
        tags = reduce(lambda a, b: a + b, self.book_tags.values(), [])
        if tags:
            return self.tag_filter(tags)
        else:
            return None

    def part_filter(self):
        """
        This filter can be used to look for book parts.
        It filters on book id and/or themes.
        """
        fs = []
        if self.part_tags:
            fs.append(self.tag_filter(self.part_tags, field='themes'))

        if self._books != []:
            bf = BooleanFilter()
            for b in self._books:
                id_filter = NumericRangeFilter.newIntRange('book_id', b.id, b.id, True, True)
                bf.add(FilterClause(id_filter, BooleanClause.Occur.SHOULD))
            fs.append(bf)

        return Search.chain_filters(fs)

    def should_search_for_book(self):
        return self._books == []

    def just_search_in(self, all):
        """Holds logic to figure out which indexes should be search, when we have some hinst already"""
        some = []
        for field in all:
            if field == 'authors' and 'author' in self.book_tags:
                continue
            if field == 'title' and self._books != []:
                continue
            if (field == 'themes' or field == 'themes_pl') and self.part_tags:
                continue
            some.append(field)
        return some


class Search(SolrIndex):
    """
    Search facilities.
    """
    def __init__(self, default_field="text"):
        IndexStore.__init__(self)
        self.analyzer = WLAnalyzer()  # PolishAnalyzer(Version.LUCENE_34)
        # self.analyzer = WLAnalyzer()
        reader = IndexReader.open(self.store, True)
        self.searcher = IndexSearcher(reader)
        self.parser = QueryParser(Version.LUCENE_34, default_field,
                                  self.analyzer)

        self.parent_filter = TermsFilter()
        self.parent_filter.addTerm(Term("is_book", "true"))
        index_changed.connect(self.reopen)

    def close(self):
        reader = self.searcher.getIndexReader()
        self.searcher.close()
        reader.close()
        super(Search, self).close()
        index_changed.disconnect(self.reopen)

    def reopen(self, **unused):
        reader = self.searcher.getIndexReader()
        rdr = reader.reopen()
        if not rdr.equals(reader):
            log.debug('Reopening index')
            oldsearch = self.searcher
            self.searcher = IndexSearcher(rdr)
            oldsearch.close()
            reader.close()

    def query(self, query):
        """Parse query in default Lucene Syntax. (for humans)
        """
        return self.parser.parse(query)

    def simple_search(self, query, max_results=50):
        """Runs a query for books using lucene syntax. (for humans)
        Returns (books, total_hits)
        """

        tops = self.searcher.search(self.query(query), max_results)
        bks = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            bks.append(catalogue.models.Book.objects.get(id=doc.get("book_id")))
        return (bks, tops.totalHits)

    def get_tokens(self, searched, field='text', cached=None):
        """returns tokens analyzed by a proper (for a field) analyzer
        argument can be: StringReader, string/unicode, or tokens. In the last case
        they will just be returned (so we can reuse tokens, if we don't change the analyzer)
        """
        if cached is not None and field in cached:
            return cached[field]

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

        if cached is not None:
            cached[field] = toks

        return toks

    @staticmethod
    def fuzziness(fuzzy):
        """Helper method to sanitize fuzziness"""
        if not fuzzy:
            return None
        if isinstance(fuzzy, float) and fuzzy > 0.0 and fuzzy <= 1.0:
            return fuzzy
        else:
            return 0.5

    def make_phrase(self, tokens, field='text', slop=2, fuzzy=False):
        """
        Return a PhraseQuery with a series of tokens.
        """
        if fuzzy:
            phrase = MultiPhraseQuery()
            for t in tokens:
                term = Term(field, t)
                fuzzterm = FuzzyTermEnum(self.searcher.getIndexReader(), term, self.fuzziness(fuzzy))
                fuzzterms = []

                while True:
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

    @staticmethod
    def make_term_query(tokens, field='text', modal='BooleanClause.Occur.SHOULD XXX', fuzzy=False):
        """
        Returns term queries joined by boolean query.
        modal - applies to boolean query
        fuzzy - should the query by fuzzy.
        """
        q = BooleanQuery()
        for t in tokens:
            term = Term(field, t)
            if fuzzy:
                term = FuzzyQuery(term, self.fuzziness(fuzzy))
            else:
                term = TermQuery(term)
            q.add(BooleanClause(term, modal))
        return q

    def search_phrase(self, searched, field, book=True, max_results=20, fuzzy=False,
                      filters=None, tokens_cache=None, boost=None, snippets=False, slop=2):
        if filters is None: filters = []
        if tokens_cache is None: tokens_cache = {}

        tokens = self.get_tokens(searched, field, cached=tokens_cache)

        query = self.make_phrase(tokens, field=field, fuzzy=fuzzy, slop=slop)
        if book:
            filters.append(self.term_filter(Term('is_book', 'true')))
        top = self.searcher.search(query, self.chain_filters(filters), max_results)

        return [SearchResult(self, found, snippets=(snippets and self.get_snippets(found, query) or None), searched=searched) for found in top.scoreDocs]

    def search_some(self, searched, fields, book=True, max_results=20, fuzzy=False,
                    filters=None, tokens_cache=None, boost=None, snippets=True):
        if filters is None: filters = []
        if tokens_cache is None: tokens_cache = {}

        if book:
            filters.append(self.term_filter(Term('is_book', 'true')))

        query = BooleanQuery()

        for fld in fields:
            tokens = self.get_tokens(searched, fld, cached=tokens_cache)

            query.add(BooleanClause(self.make_term_query(tokens, field=fld,
                                fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

        top = self.searcher.search(query, self.chain_filters(filters), max_results)

        return [SearchResult(self, found, searched=searched, tokens_cache=tokens_cache,
                             snippets=(snippets and self.get_snippets(found, query) or None)) for found in top.scoreDocs]

    def search_perfect_book(self, searched, max_results=20, fuzzy=False, hint=None):
        """
        Search for perfect book matches. Just see if the query matches with some author or title,
        taking hints into account.
        """
        fields_to_search = ['authors', 'title']
        only_in = None
        if hint:
            if not hint.should_search_for_book():
                return []
            fields_to_search = hint.just_search_in(fields_to_search)
            only_in = hint.book_filter()

        qrys = [self.make_phrase(self.get_tokens(searched, field=fld), field=fld, fuzzy=fuzzy) for fld in fields_to_search]

        books = []
        for q in qrys:
            top = self.searcher.search(q,
                self.chain_filters([only_in, self.term_filter(Term('is_book', 'true'))]),
                max_results)
            for found in top.scoreDocs:
                books.append(SearchResult(self, found, how_found="search_perfect_book"))
        return books

    def search_book(self, searched, max_results=20, fuzzy=False, hint=None):
        fields_to_search = ['tags', 'authors', 'title']

        only_in = None
        if hint:
            if not hint.should_search_for_book():
                return []
            fields_to_search = hint.just_search_in(fields_to_search)
            only_in = hint.book_filter()

        tokens = self.get_tokens(searched, field='SIMPLE')

        q = BooleanQuery()

        for fld in fields_to_search:
            q.add(BooleanClause(self.make_term_query(tokens, field=fld,
                                fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

        books = []
        top = self.searcher.search(q,
                                   self.chain_filters([only_in, self.term_filter(Term('is_book', 'true'))]),
            max_results)
        for found in top.scoreDocs:
            books.append(SearchResult(self, found, how_found="search_book"))

        return books

    def search_perfect_parts(self, searched, max_results=20, fuzzy=False, hint=None):
        """
        Search for book parts which contains a phrase perfectly matching (with a slop of 2, default for make_phrase())
        some part/fragment of the book.
        """
        qrys = [self.make_phrase(self.get_tokens(searched), field=fld, fuzzy=fuzzy) for fld in ['text']]

        flt = None
        if hint:
            flt = hint.part_filter()

        books = []
        for q in qrys:
            top = self.searcher.search(q,
                                       self.chain_filters([self.term_filter(Term('is_book', 'true'), inverse=True),
                                                           flt]),
                                       max_results)
            for found in top.scoreDocs:
                books.append(SearchResult(self, found, snippets=self.get_snippets(found, q), how_found='search_perfect_parts'))

        return books

    def search_everywhere(self, searched, max_results=20, fuzzy=False, hint=None, tokens_cache=None):
        """
        Tries to use search terms to match different fields of book (or its parts).
        E.g. one word can be an author survey, another be a part of the title, and the rest
        are some words from third chapter.
        """
        if tokens_cache is None: tokens_cache = {}
        books = []
        only_in = None

        if hint:
            only_in = hint.part_filter()

        # content only query : themes x content
        q = BooleanQuery()

        tokens_pl = self.get_tokens(searched, field='text', cached=tokens_cache)
        tokens = self.get_tokens(searched, field='SIMPLE', cached=tokens_cache)

        # only search in themes when we do not already filter by themes
        if hint is None or hint.just_search_in(['themes']) != []:
            q.add(BooleanClause(self.make_term_query(tokens_pl, field='themes_pl',
                                                     fuzzy=fuzzy), BooleanClause.Occur.MUST))

        q.add(BooleanClause(self.make_term_query(tokens_pl, field='text',
                                                 fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

        topDocs = self.searcher.search(q, only_in, max_results)
        for found in topDocs.scoreDocs:
            books.append(SearchResult(self, found, how_found='search_everywhere_themesXcontent', searched=searched))

        # query themes/content x author/title/tags
        q = BooleanQuery()
        in_content = BooleanQuery()
        in_meta = BooleanQuery()

        for fld in ['themes_pl', 'text']:
            in_content.add(BooleanClause(self.make_term_query(tokens_pl, field=fld, fuzzy=False), BooleanClause.Occur.SHOULD))

        for fld in ['tags', 'authors', 'title']:
            in_meta.add(BooleanClause(self.make_term_query(tokens, field=fld, fuzzy=False), BooleanClause.Occur.SHOULD))

        q.add(BooleanClause(in_content, BooleanClause.Occur.MUST))
        q.add(BooleanClause(in_meta, BooleanClause.Occur.SHOULD))

        topDocs = self.searcher.search(q, only_in, max_results)
        for found in topDocs.scoreDocs:
            books.append(SearchResult(self, found, how_found='search_everywhere', searched=searched))

        return books

    # def multisearch(self, query, max_results=50):
    #     """
    #     Search strategy:
    #     - (phrase) OR -> content
    #                   -> title
    #                   -> authors
    #     - (keywords)  -> authors
    #                   -> motyw
    #                   -> tags
    #                   -> content
    #     """
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

        # return None

    def get_snippets(self, scoreDoc, query, field='text'):
        """
        Returns a snippet for found scoreDoc.
        """
        htmlFormatter = SimpleHTMLFormatter()
        highlighter = Highlighter(htmlFormatter, QueryScorer(query))

        stored = self.searcher.doc(scoreDoc.doc)

        position = stored.get('snippets_position')
        length = stored.get('snippets_length')
        if position is None or length is None:
            return None
        revision = stored.get('snippets_revision')
        if revision: revision = int(revision)

        # locate content.
        book_id = int(stored.get('book_id'))
        snippets = Snippets(book_id, revision=revision)

        try:
            snippets.open()
        except IOError, e:
            log.error("Cannot open snippet file for book id = %d [rev=%d], %s" % (book_id, revision, e))
            return []

        try:
            try:
                text = snippets.get((int(position),
                                     int(length)))
            finally:
                snippets.close()

            tokenStream = TokenSources.getAnyTokenStream(self.searcher.getIndexReader(), scoreDoc.doc, field, self.analyzer)
            #  highlighter.getBestTextFragments(tokenStream, text, False, 10)
            snip = highlighter.getBestFragments(tokenStream, text, 3, "...")

        except Exception, e:
            e2 = e
            if hasattr(e, 'getJavaException'):
                e2 = unicode(e.getJavaException())
            raise Exception("Problem fetching snippets for book %d, @%d len=%d" % (book_id, int(position), int(length)),
                e2)
        return snip

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

    def search_tags(self, query, filt=None, max_results=40, pdcounter=False):
        """
        Search for Tag objects using query.
        """
        if not pdcounter:
            filters = self.chain_filters([filt, self.term_filter(Term('is_pdcounter', 'true'), inverse=True)])
        tops = self.searcher.search(query, filt, max_results)

        tags = []
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            is_pdcounter = doc.get('is_pdcounter')
            category = doc.get('tag_category')
            try:
                if is_pdcounter == 'true':
                    if category == 'pd_author':
                        tag = PDCounterAuthor.objects.get(id=doc.get('tag_id'))
                    elif category == 'pd_book':
                        tag = PDCounterBook.objects.get(id=doc.get('tag_id'))
                        tag.category = 'pd_book'  # make it look more lik a tag.
                    else:
                        print "Warning. cannot get pdcounter tag_id=%d from db; cat=%s" % (int(doc.get('tag_id')), category)
                else:
                    tag = catalogue.models.Tag.objects.get(id=doc.get("tag_id"))
                    # don't add the pdcounter tag if same tag already exists

                tags.append(tag)

            except catalogue.models.Tag.DoesNotExist: pass
            except PDCounterAuthor.DoesNotExist: pass
            except PDCounterBook.DoesNotExist: pass

        log.debug('search_tags: %s' % tags)

        return tags

    def search_books(self, query, filt=None, max_results=10):
        """
        Searches for Book objects using query
        """
        bks = []
        tops = self.searcher.search(query, filt, max_results)
        for found in tops.scoreDocs:
            doc = self.searcher.doc(found.doc)
            try:
                bks.append(catalogue.models.Book.objects.get(id=doc.get("book_id")))
            except catalogue.models.Book.DoesNotExist: pass
        return bks

    def make_prefix_phrase(self, toks, field):
        q = MultiPhraseQuery()
        for i in range(len(toks)):
            t = Term(field, toks[i])
            if i == len(toks) - 1:
                pterms = Search.enum_to_array(PrefixTermEnum(self.searcher.getIndexReader(), t))
                if pterms:
                    q.add(pterms)
                else:
                    q.add(t)
            else:
                q.add(t)
        return q

    @staticmethod
    def term_filter(term, inverse=False):
        only_term = TermsFilter()
        only_term.addTerm(term)

        if inverse:
            neg = BooleanFilter()
            neg.add(FilterClause(only_term, BooleanClause.Occur.MUST_NOT))
            only_term = neg

        return only_term

    def hint_tags(self, string, max_results=50, pdcounter=True, prefix=True, fuzzy=False):
        """
        Return auto-complete hints for tags
        using prefix search.
        """
        toks = self.get_tokens(string, field='SIMPLE')
        top = BooleanQuery()

        for field in ['tag_name', 'tag_name_pl']:
            if prefix:
                q = self.make_prefix_phrase(toks, field)
            else:
                q = self.make_term_query(toks, field, fuzzy=fuzzy)
            top.add(BooleanClause(q, BooleanClause.Occur.SHOULD))

        no_book_cat = self.term_filter(Term("tag_category", "book"), inverse=True)

        return self.search_tags(top, no_book_cat, max_results=max_results, pdcounter=pdcounter)

    def hint_books(self, string, max_results=50, prefix=True, fuzzy=False):
        """
        Returns auto-complete hints for book titles
        Because we do not index 'pseudo' title-tags.
        Prefix search.
        """
        toks = self.get_tokens(string, field='SIMPLE')

        if prefix:
            q = self.make_prefix_phrase(toks, 'title')
        else:
            q = self.make_term_query(toks, 'title', fuzzy=fuzzy)

        return self.search_books(q, self.term_filter(Term("is_book", "true")), max_results=max_results)

    @staticmethod
    def chain_filters(filters, op='XXXChainedFilter.AND'):
        """
        Chains a filter list together
        """
        filters = filter(lambda x: x is not None, filters)
        if not filters or filters is []:
            return None
        chf = ChainedFilter(JArray('object')(filters, Filter), op)
        return chf

    def filtered_categories(self, tags):
        """
        Return a list of tag categories, present in tags list.
        """
        cats = {}
        for t in tags:
            cats[t.category] = True
        return cats.keys()

    def hint(self):
        return Hint(self)
