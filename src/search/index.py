# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings

import os
import re
from librarian import dcparser
from librarian.parser import WLDocument
from lxml import etree
import catalogue.models
from pdcounter.models import Author as PDCounterAuthor, BookStub as PDCounterBook
from itertools import chain
import sunburnt
import custom
import operator
import logging
from wolnelektury.utils import makedirs

log = logging.getLogger('search')


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
        makedirs(os.path.join(settings.SEARCH_INDEX, self.SNIPPET_DIR))
        self.book_id = book_id
        self.revision = revision
        self.file = None
        self.position = None

    @property
    def path(self):
        if self.revision:
            fn = "%d.%d" % (self.book_id, self.revision)
        else:
            fn = "%d" % self.book_id

        return os.path.join(settings.SEARCH_INDEX, self.SNIPPET_DIR, fn)

    def open(self, mode='r'):
        """
        Open the snippet file. Call .close() afterwards.
        """
        if 'b' not in mode:
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
        if self.file:
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
        super(Index, self).__init__(mode='rw')

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
        log.debug("Indexing tags")
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
            self.delete_query(*tag_qs)
        else:  # all
            q = self.index.Q(tag_id__any=True)
            self.delete_query(q)

        if not remove_only:
            # then add them [all or just one passed]
            if not tags:
                tags = chain(
                    catalogue.models.Tag.objects.exclude(category='set'),
                    PDCounterAuthor.objects.all(),
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

    def create_book_doc(self, book):
        """
        Create a lucene document referring book id.
        """
        doc = {'book_id': int(book.id)}
        if book.parent is not None:
            doc['parent_id'] = int(book.parent.id)
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
        meta_fields = self.extract_metadata(book, book_info, dc_only=[
            'source_name', 'authors', 'translators', 'title', 'epochs', 'kinds', 'genres'])
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

        for tag_name in ('translators', 'epochs', 'kinds', 'genres'):
            if tag_name in meta_fields:
                book_fields[tag_name] = meta_fields[tag_name]

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
        'uwaga', 'extra', 'nota_red',
        'zastepnik_tekstu', 'sekcja_asterysk', 'separator_linia', 'zastepnik_wersu',
        'didaskalia',
        'naglowek_aktu', 'naglowek_sceny', 'naglowek_czesc',
        ]

    footnote_tags = ['pa', 'pt', 'pr', 'pe']

    skip_header_tags = ['autor_utworu', 'nazwa_utworu', 'dzielo_nadrzedne',
                        '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF']

    published_date_re = re.compile("([0-9]+)[\]. ]*$")

    def extract_metadata(self, book, book_info=None, dc_only=None):
        """
        Extract metadata from book and returns a map of fields keyed by fieldname
        """
        fields = {}

        if book_info is None:
            book_info = dcparser.parse(open(book.xml_file.path))

        fields['slug'] = book.slug
        fields['tags'] = [t.name for t in book.tags]
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
        if not pd:
            pd = ""
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

    def index_content(self, book, book_fields):
        """
        Walks the book XML and extract content from it.
        Adds parts for each header tag and for each fragment.
        """
        wld = WLDocument.from_file(book.xml_file.path, parse_dublincore=False)
        root = wld.edoc.getroot()

        master = self.get_master(root)
        if master is None:
            return []

        def walker(node):
            if node.tag not in self.ignore_content_tags:
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
            # separator = [u" ", u"\t", u".", u";", u","]
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
            doc['uid'] = "part%s-%s-%s-%s" % (
                book.id, doc['header_index'], doc['header_span'], doc.get('fragment_anchor', ''))
            return doc

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

                for start, text, end in walker(header):
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
                        footnote = []

                    # handle fragments and themes.
                    if start is not None and start.tag == 'begin':
                        fid = start.attrib['id'][1:]
                        fragments[fid] = {
                            'text': [], 'themes': [], 'start_section': position, 'start_header': header.tag}

                    # themes for this fragment
                    elif start is not None and start.tag == 'motyw':
                        fid = start.attrib['id'][1:]
                        handle_text.append(lambda text: None)
                        if start.text is not None:
                            fragments[fid]['themes'] += map(unicode.strip, map(unicode, (start.text.split(','))))
                    elif end is not None and end.tag == 'motyw':
                        handle_text.pop()

                    elif start is not None and start.tag == 'end':
                        fid = start.attrib['id'][1:]
                        if fid not in fragments:
                            continue  # a broken <end> node, skip it
                        frag = fragments[fid]
                        if not frag['themes']:
                            continue  # empty themes list.
                        del fragments[fid]

                        doc = add_part(snippets,
                                       header_type=frag['start_header'],
                                       header_index=frag['start_section'],
                                       header_span=position - frag['start_section'] + 1,
                                       fragment_anchor=fid,
                                       text=fix_format(frag['text']),
                                       themes=frag['themes'])
                        self.index.add(doc)

                        # Collect content.

                    if text is not None and handle_text is not []:
                        hdl = handle_text[-1]
                        hdl(text)

                        # in the end, add a section text.
                doc = add_part(snippets, header_index=position,
                               header_type=header.tag, text=fix_format(content))

                self.index.add(doc)

        finally:
            snippets.close()


class SearchResult(object):
    def __init__(self, doc, how_found=None, query_terms=None):
        self.boost = 1.0
        self._hits = []
        self._processed_hits = None  # processed hits
        self.snippets = []
        self.query_terms = query_terms
        self._book = None

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
            snippets_rev = doc.get('snippets_revision', None)

            hit = (sec + (header_span,), fragment, self._score, {
                'how_found': how_found,
                'snippets_pos': snippets_pos,
                'snippets_revision': snippets_rev,
                'themes': doc.get('themes', []),
                'themes_pl': doc.get('themes_pl', [])
                })

            self._hits.append(hit)

    def __unicode__(self):
        return u"<SR id=%d %d(%d) hits score=%f %d snippets>" % \
            (self.book_id, len(self._hits),
             len(self._processed_hits) if self._processed_hits else -1,
             self._score, len(self.snippets))

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
        if self._book is not None:
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
            lambda f: f[self.POSITION][self.POSITION_INDEX] <= s[self.POSITION][self.POSITION_INDEX] <
                      f[self.POSITION][self.POSITION_INDEX] + f[self.POSITION][self.POSITION_SPAN], frags)), sect)

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
            themes_hit = set()
            if self.query_terms is not None:
                for i in range(0, len(f[self.OTHER]['themes'])):
                    tms = f[self.OTHER]['themes'][i].split(r' +') + f[self.OTHER]['themes_pl'][i].split(' ')
                    tms = map(unicode.lower, tms)
                    for qt in self.query_terms:
                        if qt in tms:
                            themes_hit.add(f[self.OTHER]['themes'][i])
                            break

            def theme_by_name(n):
                th = filter(lambda t: t.name == n, themes)
                if th:
                    return th[0]
                else:
                    return None
            themes_hit = filter(lambda a: a is not None, map(theme_by_name, themes_hit))

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
        except (IndexError, KeyError):
            return None


class Search(SolrIndex):
    """
    Search facilities.
    """
    def __init__(self, default_field="text"):
        super(Search, self).__init__(mode='r')

    def make_term_query(self, query, field='text', modal=operator.or_):
        """
        Returns term queries joined by boolean query.
        modal - applies to boolean query
        fuzzy - should the query by fuzzy.
        """
        if query is None:
            query = ''
        q = self.index.Q()
        q = reduce(modal, map(lambda s: self.index.Q(**{field: s}), query.split(r" ")), q)

        return q

    def search_words(self, words, fields, book=True):
        filters = []
        for word in words:
            word_filter = None
            for field in fields:
                q = self.index.Q(**{field: word})
                if word_filter is None:
                    word_filter = q
                else:
                    word_filter |= q
            filters.append(word_filter)
        if book:
            query = self.index.query(is_book=True)
        else:
            query = self.index.query()
        query = self.apply_filters(query, filters).field_limit(score=True, all_fields=True)
        return [SearchResult(found, how_found='search_words', query_terms=words) for found in query.execute()]

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
                snip = self.index.highlight(text=text, field=field, q=query)
                if snip not in snips:
                    snips[idx] = snip
                    if snip:
                        num -= 1
                idx += 1

        except IOError, e:
            book = catalogue.models.Book.objects.filter(id=book_id)
            if not book:
                log.error("Book does not exist for book id = %d" % book_id)
            elif not book.get().children.exists():
                log.error("Cannot open snippet file for book id = %d [rev=%s], %s" % (book_id, revision, e))
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
        qu = self.index.query(q)

        return self.search_tags(qu, pdcounter=pdcounter)

    def search_tags(self, query, filters=None, pdcounter=False):
        """
        Search for Tag objects using query.
        """
        if not filters:
            filters = []
        if not pdcounter:
            filters.append(~self.index.Q(is_pdcounter=True))
        res = self.apply_filters(query, filters).execute()

        tags = []
        pd_tags = []

        for doc in res:
            is_pdcounter = doc.get('is_pdcounter', False)
            category = doc.get('tag_category')
            try:
                if is_pdcounter:
                    if category == 'pd_author':
                        tag = PDCounterAuthor.objects.get(id=doc.get('tag_id'))
                    else:  # category == 'pd_book':
                        tag = PDCounterBook.objects.get(id=doc.get('tag_id'))
                        tag.category = 'pd_book'  # make it look more lik a tag.
                    pd_tags.append(tag)
                else:
                    tag = catalogue.models.Tag.objects.get(id=doc.get("tag_id"))
                    tags.append(tag)

            except catalogue.models.Tag.DoesNotExist:
                pass
            except PDCounterAuthor.DoesNotExist:
                pass
            except PDCounterBook.DoesNotExist:
                pass

        tags_slugs = set(map(lambda t: t.slug, tags))
        tags = tags + filter(lambda t: t.slug not in tags_slugs, pd_tags)

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
            q |= self.index.Q(title_orig=query + "*")
        else:
            q |= self.make_term_query(query, field='title')
            q |= self.make_term_query(query, field='title_orig')
        qu = self.index.query(q)
        only_books = self.index.Q(is_book=True)
        return self.search_books(qu, [only_books])

    def search_books(self, query, filters=None, max_results=10):
        """
        Searches for Book objects using query
        """
        bks = []
        bks_found = set()
        query = query.query(is_book=True)
        res = self.apply_filters(query, filters).field_limit(['book_id'])
        for r in res:
            try:
                bid = r['book_id']
                if bid not in bks_found:
                    bks.append(catalogue.models.Book.objects.get(id=bid))
                    bks_found.add(bid)
            except catalogue.models.Book.DoesNotExist:
                pass
        return bks

    @staticmethod
    def apply_filters(query, filters):
        """
        Apply filters to a query
        """
        if filters is None:
            filters = []
        filters = filter(lambda x: x is not None, filters)
        for f in filters:
            query = query.query(f)
        return query


if getattr(settings, 'SEARCH_MOCK', False):
    from .mock_search import Search
