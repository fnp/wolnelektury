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
import custom
import operator


class SolrIndex(object):
    def __init__(self, mode=None):
        self.index = custom.CustomSolrInterface(settings.SOLR, mode=mode)


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
                st += rows
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
                        "is_pdcounter": True,
                        "uid": "tag%d_pd_a" % tag.id
                        }
                elif isinstance(tag, PDCounterBook):
                    doc = {
                        "tag_id": int(tag.id),
                        "tag_name": tag.title,
                        "tag_name_pl": tag.title,
                        "tag_category": 'pd_book',
                        "is_pdcounter": True,
                        "uid": "tag%d_pd_b" % tag.id
                        }
                else:
                    doc = {
                        "tag_id": int(tag.id),
                        "tag_name": tag.name,
                        "tag_name_pl": tag.name,
                        "tag_category": tag.category,
                        "is_pdcounter": False,
                        "uid": "tag%d" % tag.id
                        }
                self.index.add(doc)
                print "%s %s" % (doc['tag_name'], doc['tag_category'])

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
        book_fields = {
            'title': meta_fields['title'],
            'authors': meta_fields['authors'],
            'published_date': meta_fields['published_date']
            }
        if 'translators' in meta_fields:
            book_fields['translators'] = meta_fields['translators']

        self.index_content(book, book_fields=book_fields)

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
                                         doc.get('fragment_anchor', ''))
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
    def __init__(self, doc, how_found=None, query=None):
        #        self.search = search
        self.boost = 1.0
        self._hits = []
        self._processed_hits = None  # processed hits
        self.snippets = []

        if 'score' in doc:
            self._score = doc['score']
        else:
            self._score = 0

        self.book_id = int(doc["book_id"])

        try:
            self.published_date = int(doc.get("published_date"))
        except ValueError:
            self.published_date = 0

        # content hits
        header_type = doc.get("header_type", None)
        # we have a content hit in some header of fragment
        if header_type is not None:
            sec = (header_type, int(doc["header_index"]))
            header_span = doc['header_span']
            header_span = header_span is not None and int(header_span) or 1
            fragment = doc.get("fragment_anchor", None)
            snippets_pos = (doc['snippets_position'], doc['snippets_length'])
            snippets_rev = doc['snippets_revision']

            hit = (sec + (header_span,), fragment, self._score, {
                'how_found': how_found,
                'snippets_pos': snippets_pos,
                'snippets_revision': snippets_rev
                })

            self._hits.append(hit)

    def __unicode__(self):
        return u"<SR id=%d %d(%d) hits score=%f %d snippets" % \
            (self.book_id, len(self._hits), self._processed_hits and len(self._processed_hits) or -1, self._score, len(self.snippets))
    
    def __str__(self):
        return unicode(self).encode('utf-8')

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
        self._book = catalogue.models.Book.objects.get(id=self.book_id)
        return self._book

    book = property(get_book)

    POSITION = 0
    FRAGMENT = 1
    POSITION_INDEX = 1
    POSITION_SPAN = 2
    SCORE = 2
    OTHER = 3

    @property
    def hits(self):
        if self._processed_hits is not None:
            return self._processed_hits

        # to sections and fragments
        frags = filter(lambda r: r[self.FRAGMENT] is not None, self._hits)

        sect = filter(lambda r: r[self.FRAGMENT] is None, self._hits)

        # sections not covered by fragments
        sect = filter(lambda s: 0 == len(filter(
            lambda f: s[self.POSITION][self.POSITION_INDEX] >= f[self.POSITION][self.POSITION_INDEX]
            and s[self.POSITION][self.POSITION_INDEX] < f[self.POSITION][self.POSITION_INDEX] + f[self.POSITION][self.POSITION_SPAN],
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
        frags = remove_duplicates(frags, lambda f: f[self.FRAGMENT], lambda a, b: cmp(a[self.SCORE], b[self.SCORE]))
        # frags = remove_duplicates(frags, lambda f: f[OTHER]['snippet_pos'] and f[OTHER]['snippet_pos'] or f[FRAGMENT],
        #                           lambda a, b: cmp(a[SCORE], b[SCORE]))

        # remove duplicate sections
        sections = {}

        for s in sect:
            si = s[self.POSITION][self.POSITION_INDEX]
            # skip existing
            if si in sections:
                if sections[si]['score'] >= s[self.SCORE]:
                    continue

            m = {'score': s[self.SCORE],
                 'section_number': s[self.POSITION][self.POSITION_INDEX] + 1,
                 }
            m.update(s[self.OTHER])
            sections[si] = m

        hits = sections.values()

        for f in frags:
            try:
                frag = catalogue.models.Fragment.objects.get(anchor=f[self.FRAGMENT], book__id=self.book_id)
            except catalogue.models.Fragment.DoesNotExist:
                # stale index
                continue

            # Figure out if we were searching for a token matching some word in theme name.
            themes = frag.tags.filter(category='theme')
            themes_hit = []
            # if self.searched is not None:
            #     tokens = self.search.get_tokens(self.searched, 'POLISH', cached=self.tokens_cache)
            #     for theme in themes:
            #         name_tokens = self.search.get_tokens(theme.name, 'POLISH')
            #         for t in tokens:
            #             if t in name_tokens:
            #                 if not theme in themes_hit:
            #                     themes_hit.append(theme)
            #                 break

            m = {'score': f[self.SCORE],
                 'fragment': frag,
                 'section_number': f[self.POSITION][self.POSITION_INDEX] + 1,
                 'themes': themes,
                 'themes_hit': themes_hit
                 }
            m.update(f[self.OTHER])
            hits.append(m)

        hits.sort(lambda a, b: cmp(a['score'], b['score']), reverse=True)

        self._processed_hits = hits

        return hits

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

    def __len__(self):
        return len(self.hits)

    def snippet_pos(self, idx=0):
        return self.hits[idx]['snippets_pos']

    def snippet_revision(self, idx=0):
        try:
            return self.hits[idx]['snippets_revision']
        except:
            return None


class Search(SolrIndex):
    """
    Search facilities.
    """
    def __init__(self, default_field="text"):
        super(Search, self).__init__()

    # def get_tokens(self, searched, field='text', cached=None):
    #     """returns tokens analyzed by a proper (for a field) analyzer
    #     argument can be: StringReader, string/unicode, or tokens. In the last case
    #     they will just be returned (so we can reuse tokens, if we don't change the analyzer)
    #     """
    #     if cached is not None and field in cached:
    #         return cached[field]

    #     if isinstance(searched, str) or isinstance(searched, unicode):
    #         searched = StringReader(searched)
    #     elif isinstance(searched, list):
    #         return searched

    #     searched.reset()
    #     tokens = self.analyzer.reusableTokenStream(field, searched)
    #     toks = []
    #     while tokens.incrementToken():
    #         cta = tokens.getAttribute(CharTermAttribute.class_)
    #         toks.append(cta.toString())

    #     if cached is not None:
    #         cached[field] = toks

    #     return toks

    # @staticmethod
    # def fuzziness(fuzzy):
    #     """Helper method to sanitize fuzziness"""
    #     if not fuzzy:
    #         return None
    #     if isinstance(fuzzy, float) and fuzzy > 0.0 and fuzzy <= 1.0:
    #         return fuzzy
    #     else:
    #         return 0.5

    # def make_phrase(self, tokens, field='text', slop=2, fuzzy=False):
    #     """
    #     Return a PhraseQuery with a series of tokens.
    #     """
    #     if fuzzy:
    #         phrase = MultiPhraseQuery()
    #         for t in tokens:
    #             term = Term(field, t)
    #             fuzzterm = FuzzyTermEnum(self.searcher.getIndexReader(), term, self.fuzziness(fuzzy))
    #             fuzzterms = []

    #             while True:
    #                 ft = fuzzterm.term()
    #                 if ft:
    #                     fuzzterms.append(ft)
    #                 if not fuzzterm.next(): break
    #             if fuzzterms:
    #                 phrase.add(JArray('object')(fuzzterms, Term))
    #             else:
    #                 phrase.add(term)
    #     else:
    #         phrase = PhraseQuery()
    #         phrase.setSlop(slop)
    #         for t in tokens:
    #             term = Term(field, t)
    #             phrase.add(term)
    #     return phrase

    def make_term_query(self, query, field='text', modal=operator.or_):
        """
        Returns term queries joined by boolean query.
        modal - applies to boolean query
        fuzzy - should the query by fuzzy.
        """
        q = self.index.Q()
        q = reduce(modal, map(lambda s: self.index.Q(**{field: s}),
                        query.split(r" ")), q)

        return q

    def search_phrase(self, searched, field='text', book=False,
                      filters=None,
                      snippets=False):
        if filters is None: filters = []
        if book: filters.append(self.index.Q(is_book=True))

        q = self.index.query(**{field: searched})
        q = self.apply_filters(q, filters).field_limit(score=True, all_fields=True)
        res = q.execute()
        return [SearchResult(found, how_found=u'search_phrase') for found in res]

    def search_some(self, searched, fields, book=True,
                    filters=None,
                    snippets=True):
        assert isinstance(fields, list)
        if filters is None: filters = []
        if book: filters.append(self.index.Q(is_book=True))

        query = self.index.Q()

        for fld in fields:
            query = self.index.Q(query | self.make_term_query(searched, fld))

        query = self.index.query(query)
        query = self.apply_filters(query, filters).field_limit(score=True, all_fields=True)
        res = query.execute()
        return [SearchResult(found, how_found='search_some') for found in res]

    # def search_perfect_book(self, searched, max_results=20, fuzzy=False, hint=None):
    #     """
    #     Search for perfect book matches. Just see if the query matches with some author or title,
    #     taking hints into account.
    #     """
    #     fields_to_search = ['authors', 'title']
    #     only_in = None
    #     if hint:
    #         if not hint.should_search_for_book():
    #             return []
    #         fields_to_search = hint.just_search_in(fields_to_search)
    #         only_in = hint.book_filter()

    #     qrys = [self.make_phrase(self.get_tokens(searched, field=fld), field=fld, fuzzy=fuzzy) for fld in fields_to_search]

    #     books = []
    #     for q in qrys:
    #         top = self.searcher.search(q,
    #             self.chain_filters([only_in, self.term_filter(Term('is_book', 'true'))]),
    #             max_results)
    #         for found in top.scoreDocs:
    #             books.append(SearchResult(self, found, how_found="search_perfect_book"))
    #     return books

    # def search_book(self, searched, max_results=20, fuzzy=False, hint=None):
    #     fields_to_search = ['tags', 'authors', 'title']

    #     only_in = None
    #     if hint:
    #         if not hint.should_search_for_book():
    #             return []
    #         fields_to_search = hint.just_search_in(fields_to_search)
    #         only_in = hint.book_filter()

    #     tokens = self.get_tokens(searched, field='SIMPLE')

    #     q = BooleanQuery()

    #     for fld in fields_to_search:
    #         q.add(BooleanClause(self.make_term_query(tokens, field=fld,
    #                             fuzzy=fuzzy), BooleanClause.Occur.SHOULD))

    #     books = []
    #     top = self.searcher.search(q,
    #                                self.chain_filters([only_in, self.term_filter(Term('is_book', 'true'))]),
    #         max_results)
    #     for found in top.scoreDocs:
    #         books.append(SearchResult(self, found, how_found="search_book"))

    #     return books

    # def search_perfect_parts(self, searched, max_results=20, fuzzy=False, hint=None):
    #     """
    #     Search for book parts which contains a phrase perfectly matching (with a slop of 2, default for make_phrase())
    #     some part/fragment of the book.
    #     """
    #     qrys = [self.make_phrase(self.get_tokens(searched), field=fld, fuzzy=fuzzy) for fld in ['text']]

    #     flt = None
    #     if hint:
    #         flt = hint.part_filter()

    #     books = []
    #     for q in qrys:
    #         top = self.searcher.search(q,
    #                                    self.chain_filters([self.term_filter(Term('is_book', 'true'), inverse=True),
    #                                                        flt]),
    #                                    max_results)
    #         for found in top.scoreDocs:
    #             books.append(SearchResult(self, found, snippets=self.get_snippets(found, q), how_found='search_perfect_parts'))

    #     return books

    def search_everywhere(self, searched):
        """
        Tries to use search terms to match different fields of book (or its parts).
        E.g. one word can be an author survey, another be a part of the title, and the rest
        are some words from third chapter.
        """
        books = []
        # content only query : themes x content

        q = self.make_term_query(searched, 'text')
        q_themes = self.make_term_query(searched, 'themes_pl')

        query = self.index.query(q).query(q_themes).field_limit(score=True, all_fields=True)
        res = query.execute()

        for found in res:
            books.append(SearchResult(found, how_found='search_everywhere_themesXcontent'))

        # query themes/content x author/title/tags
        in_content = self.index.Q()
        in_meta = self.index.Q()

        for fld in ['themes_pl', 'text']:
            in_content |= self.make_term_query(searched, field=fld)

        for fld in ['tags', 'authors', 'title']:
            in_meta |= self.make_term_query(searched, field=fld)

        q = in_content & in_meta
        res = self.index.query(q).field_limit(score=True, all_fields=True).execute()
        for found in res:
            books.append(SearchResult(found, how_found='search_everywhere'))

        return books

    def get_snippets(self, searchresult, query, field='text', num=1):
        """
        Returns a snippet for found scoreDoc.
        """
        maxnum = len(searchresult)
        if num is None or num < 0 or num > maxnum:
            num = maxnum
        book_id = searchresult.book_id
        revision = searchresult.snippet_revision()
        snippets = Snippets(book_id, revision=revision)
        snips = [None] * maxnum
        try:
            snippets.open()
            idx = 0
            while idx < maxnum and num > 0:
                position, length = searchresult.snippet_pos(idx)
                if position is None or length is None:
                    continue
                text = snippets.get((int(position),
                                     int(length)))
                print "== %s -- %s ==" % (query, text)
                snip = self.index.highlight(text=text, field=field, q=query)
                snips[idx] = snip
                if snip:
                    num -= 1
                idx += 1

        except IOError, e:
            log.error("Cannot open snippet file for book id = %d [rev=%d], %s" % (book_id, revision, e))
            return []
        finally:
            snippets.close()

            # remove verse end markers..
        snips = map(lambda s: s and s.replace("/\n", "\n"), snips)

        searchresult.snippets = snips
        return snips

    def hint_tags(self, query, pdcounter=True, prefix=True):
        """
        Return auto-complete hints for tags
        using prefix search.
        """
        q = self.index.Q()
        query = query.strip()
        for field in ['tag_name', 'tag_name_pl']:
            if prefix:
                q |= self.index.Q(**{field: query + "*"})
            else:
                q |= self.make_term_query(query, field=field)
        qu = self.index.query(q).exclude(tag_category="book")

        return self.search_tags(qu, pdcounter=pdcounter)

    def search_tags(self, query, filters=None, pdcounter=False):
        """
        Search for Tag objects using query.
        """
        if not filters: filters = []
        if not pdcounter:
            filters.append(~self.index.Q(is_pdcounter=True))
        res = self.apply_filters(query, filters).execute()

        tags = []
        for doc in res:
            is_pdcounter = doc.get('is_pdcounter', False)
            category = doc.get('tag_category')
            try:
                if is_pdcounter == True:
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

    def hint_books(self, query, prefix=True):
        """
        Returns auto-complete hints for book titles
        Because we do not index 'pseudo' title-tags.
        Prefix search.
        """
        q = self.index.Q()
        query = query.strip()
        if prefix:
            q |= self.index.Q(title=query + "*")
        else:
            q |= self.make_term_query(query, field='title')
        qu = self.index.query(q)
        only_books = self.index.Q(is_book=True)
        return self.search_books(qu, [only_books])

    def search_books(self, query, filters=None, max_results=10):
        """
        Searches for Book objects using query
        """
        bks = []
        res = self.apply_filters(query, filters).field_limit(['book_id'])
        for r in res:
            try:
                bks.append(catalogue.models.Book.objects.get(id=r['book_id']))
            except catalogue.models.Book.DoesNotExist: pass
        return bks
 
    # def make_prefix_phrase(self, toks, field):
    #     q = MultiPhraseQuery()
    #     for i in range(len(toks)):
    #         t = Term(field, toks[i])
    #         if i == len(toks) - 1:
    #             pterms = Search.enum_to_array(PrefixTermEnum(self.searcher.getIndexReader(), t))
    #             if pterms:
    #                 q.add(pterms)
    #             else:
    #                 q.add(t)
    #         else:
    #             q.add(t)
    #     return q

    # @staticmethod
    # def term_filter(term, inverse=False):
    #     only_term = TermsFilter()
    #     only_term.addTerm(term)

    #     if inverse:
    #         neg = BooleanFilter()
    #         neg.add(FilterClause(only_term, BooleanClause.Occur.MUST_NOT))
    #         only_term = neg

    #     return only_term



    @staticmethod
    def apply_filters(query, filters):
        """
        Apply filters to a query
        """
        if filters is None: filters = []
        filters = filter(lambda x: x is not None, filters)
        for f in filters:
            query = query.query(f)
        return query

    # def filtered_categories(self, tags):
    #     """
    #     Return a list of tag categories, present in tags list.
    #     """
    #     cats = {}
    #     for t in tags:
    #         cats[t.category] = True
    #     return cats.keys()

    # def hint(self):
    #     return Hint(self)
