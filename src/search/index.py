# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from functools import reduce, total_ordering
from itertools import chain
import logging
import operator
import os
import re
from django.conf import settings
from librarian import dcparser
import librarian.meta.types.person
import librarian.meta.types.text
from librarian.parser import WLDocument
from lxml import etree
import scorched
import catalogue.models
import picture.models
from pdcounter.models import Author as PDCounterAuthor, BookStub as PDCounterBook
from wolnelektury.utils import makedirs
from . import custom

log = logging.getLogger('search')


if os.path.isfile(settings.SOLR_STOPWORDS):
    stopwords = set(
        line.strip()
        for line in open(settings.SOLR_STOPWORDS) if not line.startswith('#'))
else:
    stopwords = set()


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
        try:
            txt = self.file.read(pos[1]).decode('utf-8')
        except:
            return ''
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

    def remove_snippets(self, book):
        book.snippet_set.all().delete()

    def add_snippet(self, book, doc):
        assert book.id == doc.pop('book_id')
        # Fragments already exist and can be indexed where they live.
        if 'fragment_anchor' in doc:
            return

        text = doc.pop('text')
        header_index = doc.pop('header_index')
        book.snippet_set.create(
            sec=header_index,
            text=text,
        )

    def delete_query(self, *queries):
        """
        index.delete(queries=...) doesn't work, so let's reimplement it
        using deletion of list of uids.
        """
        uids = set()
        for q in queries:
            if isinstance(q, scorched.search.LuceneQuery):
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
            # FIXME: With Solr API change, this doesn't work.
            #self.index.delete(uids)
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

    def remove_book(self, book, remove_snippets=True, legacy=True):
        """Removes a book from search index.
        book - Book instance."""
        if legacy:
          self.delete_query(self.index.Q(book_id=book.id))

          if remove_snippets:
            snippets = Snippets(book.id)
            snippets.remove()
        self.remove_snippets(book)

    def index_book(self, book, book_info=None, overwrite=True, legacy=True):
        """
        Indexes the book.
        Creates a lucene document for extracted metadata
        and calls self.index_content() to index the contents of the book.
        """
        if not book.xml_file: return

        if overwrite:
            # we don't remove snippets, since they might be still needed by
            # threads using not reopened index
            self.remove_book(book, remove_snippets=False, legacy=legacy)

        book_doc = self.create_book_doc(book)
        meta_fields = self.extract_metadata(book, book_info, dc_only=[
            'source_name', 'authors', 'translators', 'title', 'epochs', 'kinds', 'genres'])
        # let's not index it - it's only used for extracting publish date
        if 'source_name' in meta_fields:
            del meta_fields['source_name']

        for n, f in meta_fields.items():
            book_doc[n] = f

        book_doc['uid'] = "book%s" % book_doc['book_id']
        if legacy:
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

        self.index_content(book, book_fields=book_fields, legacy=legacy)

    master_tags = [
        'opowiadanie',
        'powiesc',
        'dramat_wierszowany_l',
        'dramat_wierszowany_lp',
        'dramat_wspolczesny', 'liryka_l', 'liryka_lp',
        'wywiad',
    ]

    ignore_content_tags = [
        'uwaga', 'extra', 'nota_red', 'abstrakt',
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
            book_info = dcparser.parse(open(book.xml_file.path, 'rb'))

        fields['slug'] = book.slug
        fields['is_book'] = True

        # validator, name
        for field in dcparser.BookInfo.FIELDS:
            if dc_only and field.name not in dc_only:
                continue
            if hasattr(book_info, field.name):
                if not getattr(book_info, field.name):
                    continue
                type_indicator = field.value_type
                if issubclass(type_indicator, librarian.meta.types.text.TextValue):
                    s = getattr(book_info, field.name)
                    if field.multiple:
                        s = ', '.join(s)
                    fields[field.name] = s
                elif issubclass(type_indicator, librarian.meta.types.person.Person):
                    p = getattr(book_info, field.name)
                    if isinstance(p, librarian.meta.types.person.Person):
                        persons = str(p)
                    else:
                        persons = ', '.join(map(str, p))
                    fields[field.name] = persons

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

    def index_content(self, book, book_fields, legacy=True):
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
            # separator = [" ", "\t", ".", ";", ","]
            if isinstance(text, list):
                # need to join it first
                text = filter(lambda s: s is not None, content)
                text = ' '.join(text)
                # for i in range(len(text)):
                #     if i > 0:
                #         if text[i][0] not in separator\
                #             and text[i - 1][-1] not in separator:
                #          text.insert(i, " ")

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
                                       text=''.join(footnote))
                        self.add_snippet(book, doc)
                        if legacy:
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
                            fragments[fid]['themes'] += map(str.strip, map(str, (start.text.split(','))))
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
                        # Add searchable fragment
                        self.add_snippet(book, doc)
                        if legacy:
                            self.index.add(doc)

                        # Collect content.

                    if text is not None and handle_text is not []:
                        hdl = handle_text[-1]
                        hdl(text)

                        # in the end, add a section text.
                doc = add_part(snippets, header_index=position,
                               header_type=header.tag, text=fix_format(content))

                self.add_snippet(book, doc)
                if legacy:
                    self.index.add(doc)

        finally:
            snippets.close()

    def remove_picture(self, picture_or_id):
        """Removes a picture from search index."""
        if isinstance(picture_or_id, picture.models.Picture):
            picture_id = picture_or_id.id
        else:
            picture_id = picture_or_id
        self.delete_query(self.index.Q(picture_id=picture_id))

    def index_picture(self, picture, picture_info=None, overwrite=True):
        """
        Indexes the picture.
        Creates a lucene document for extracted metadata
        and calls self.index_area() to index the contents of the picture.
        """
        if overwrite:
            # we don't remove snippets, since they might be still needed by
            # threads using not reopened index
            self.remove_picture(picture)

        picture_doc = {'picture_id': int(picture.id)}
        meta_fields = self.extract_metadata(picture, picture_info, dc_only=[
            'authors', 'title', 'epochs', 'kinds', 'genres'])

        picture_doc.update(meta_fields)

        picture_doc['uid'] = "picture%s" % picture_doc['picture_id']
        self.index.add(picture_doc)
        del picture_doc['is_book']
        for area in picture.areas.all():
            self.index_area(area, picture_fields=picture_doc)

    def index_area(self, area, picture_fields):
        """
        Indexes themes and objects on the area.
        """
        doc = dict(picture_fields)
        doc['area_id'] = area.id
        doc['themes'] = list(area.tags.filter(category__in=('theme', 'thing')).values_list('name', flat=True))
        doc['uid'] = 'area%s' % area.id
        self.index.add(doc)


@total_ordering
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

    @classmethod
    def from_book(cls, book, how_found=None, query_terms=None):
        doc = {
            'score': book.popularity.count,
            'book_id': book.id,
            'published_date': 0,
        }
        result = cls(doc, how_found=how_found, query_terms=query_terms)
        result._book = book
        return result

    def __str__(self):
        return "<SR id=%d %d(%d) hits score=%f %d snippets>" % \
            (self.book_id, len(self._hits),
             len(self._processed_hits) if self._processed_hits else -1,
             self._score, len(self.snippets))

    def __bytes__(self):
        return str(self).encode('utf-8')

    @property
    def score(self):
        return self._score * self.boost

    def merge(self, other):
        if self.book_id != other.book_id:
            raise ValueError("this search result is for book %d; tried to merge with %d" % (self.book_id, other.book_id))
        self._hits += other._hits
        self._score += max(other._score, 0)
        return self

    def get_book(self):
        if self._book is not None:
            return self._book
        try:
            self._book = catalogue.models.Book.objects.get(id=self.book_id, findable=True)
        except catalogue.models.Book.DoesNotExist:
            self._book = None
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

        sect = [hit for hit in self._hits if hit[self.FRAGMENT] is None]

        # sections not covered by fragments
        sect = filter(lambda s: 0 == len(list(filter(
            lambda f: f[self.POSITION][self.POSITION_INDEX] <= s[self.POSITION][self.POSITION_INDEX] <
                      f[self.POSITION][self.POSITION_INDEX] + f[self.POSITION][self.POSITION_SPAN], frags))), sect)

        def remove_duplicates(lst, keyfn, larger):
            els = {}
            for e in lst:
                eif = keyfn(e)
                if eif in els:
                    if larger(els[eif], e):
                        continue
                els[eif] = e
            return els.values()

        # remove fragments with duplicated fid's and duplicated snippets
        frags = remove_duplicates(frags, lambda f: f[self.FRAGMENT], lambda a, b: a[self.SCORE] > b[self.SCORE])

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

        hits = list(sections.values())

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
                    tms = map(str.lower, tms)
                    for qt in self.query_terms:
                        if qt in tms:
                            themes_hit.add(f[self.OTHER]['themes'][i])
                            break

            def theme_by_name(n):
                th = list(filter(lambda t: t.name == n, themes))
                if th:
                    return th[0]
                else:
                    return None
            themes_hit = list(filter(lambda a: a is not None, map(theme_by_name, themes_hit)))

            m = {'score': f[self.SCORE],
                 'fragment': frag,
                 'section_number': f[self.POSITION][self.POSITION_INDEX] + 1,
                 'themes': themes,
                 'themes_hit': themes_hit
                 }
            m.update(f[self.OTHER])
            hits.append(m)

        hits.sort(key=lambda h: h['score'], reverse=True)

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

    def get_sort_key(self):
        return (-self.score,
                self.published_date,
                self.book.sort_key_author if self.book else '',
                self.book.sort_key if self.book else '')

    def __lt__(self, other):
        return self.get_sort_key() > other.get_sort_key()

    def __eq__(self, other):
        return self.get_sort_key() == other.get_sort_key()

    def __len__(self):
        return len(self.hits)

    def snippet_pos(self, idx=0):
        return self.hits[idx]['snippets_pos']

    def snippet_revision(self, idx=0):
        try:
            return self.hits[idx]['snippets_revision']
        except (IndexError, KeyError):
            return None


@total_ordering
class PictureResult(object):
    def __init__(self, doc, how_found=None, query_terms=None):
        self.boost = 1.0
        self.query_terms = query_terms
        self._picture = None
        self._hits = []
        self._processed_hits = None

        if 'score' in doc:
            self._score = doc['score']
        else:
            self._score = 0

        self.picture_id = int(doc["picture_id"])

        if doc.get('area_id'):
            hit = (self._score, {
                'how_found': how_found,
                'area_id': doc['area_id'],
                'themes': doc.get('themes', []),
                'themes_pl': doc.get('themes_pl', []),
            })

            self._hits.append(hit)

    def __str__(self):
        return "<PR id=%d score=%f >" % (self.picture_id, self._score)

    def __repr__(self):
        return str(self)

    @property
    def score(self):
        return self._score * self.boost

    def merge(self, other):
        if self.picture_id != other.picture_id:
            raise ValueError(
                "this search result is for picture %d; tried to merge with %d" % (self.picture_id, other.picture_id))
        self._hits += other._hits
        self._score += max(other._score, 0)
        return self

    SCORE = 0
    OTHER = 1

    @property
    def hits(self):
        if self._processed_hits is not None:
            return self._processed_hits

        hits = []
        for hit in self._hits:
            try:
                area = picture.models.PictureArea.objects.get(id=hit[self.OTHER]['area_id'])
            except picture.models.PictureArea.DoesNotExist:
                # stale index
                continue
            # Figure out if we were searching for a token matching some word in theme name.
            themes_hit = set()
            if self.query_terms is not None:
                for i in range(0, len(hit[self.OTHER]['themes'])):
                    tms = hit[self.OTHER]['themes'][i].split(r' +') + hit[self.OTHER]['themes_pl'][i].split(' ')
                    tms = map(str.lower, tms)
                    for qt in self.query_terms:
                        if qt in tms:
                            themes_hit.add(hit[self.OTHER]['themes'][i])
                            break

            m = {
                'score': hit[self.SCORE],
                'area': area,
                'themes_hit': themes_hit,
            }
            m.update(hit[self.OTHER])
            hits.append(m)

        hits.sort(key=lambda h: h['score'], reverse=True)
        hits = hits[:1]
        self._processed_hits = hits
        return hits

    def get_picture(self):
        if self._picture is None:
            self._picture = picture.models.Picture.objects.get(id=self.picture_id)
        return self._picture

    picture = property(get_picture)

    @staticmethod
    def aggregate(*result_lists):
        books = {}
        for rl in result_lists:
            for r in rl:
                if r.picture_id in books:
                    books[r.picture_id].merge(r)
                else:
                    books[r.picture_id] = r
        return books.values()

    def __lt__(self, other):
        return self.score < other.score

    def __eq__(self, other):
        return self.score == other.score


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

    def search_by_author(self, words):
        from catalogue.models import Book
        books = Book.objects.filter(parent=None, findable=True).order_by('-popularity__count')
        for word in words:
            books = books.filter(cached_author__iregex='\m%s\M' % word).select_related('popularity__count')
        return [SearchResult.from_book(book, how_found='search_by_author', query_terms=words) for book in books[:30]]

    def search_words(self, words, fields, required=None, book=True, picture=False):
        if book and not picture and fields == ['authors']:
            return self.search_by_author(words)
        filters = []
        for word in words:
            if book or picture or (word not in stopwords):
                word_filter = None
                for field in fields:
                    q = self.index.Q(**{field: word})
                    if word_filter is None:
                        word_filter = q
                    else:
                        word_filter |= q
                filters.append(word_filter)
        if required:
            required_filter = None
            for field in required:
                for word in words:
                    if book or picture or (word not in stopwords):
                        q = self.index.Q(**{field: word})
                        if required_filter is None:
                            required_filter = q
                        else:
                            required_filter |= q
            filters.append(required_filter)
        if not filters:
            return []
        params = {}
        if book:
            params['is_book'] = True
        if picture:
            params['picture_id__gt'] = 0
        else:
            params['book_id__gt'] = 0
        query = self.index.query(**params)
        query = self.apply_filters(query, filters).field_limit(score=True, all_fields=True)
        result_class = PictureResult if picture else SearchResult
        return [result_class(found, how_found='search_words', query_terms=words) for found in query.execute()]

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
                if not snip and field == 'text':
                    snip = self.index.highlight(text=text, field='text_nonstem', q=query)
                if snip not in snips:
                    snips[idx] = snip
                    if snip:
                        num -= 1
                idx += 1

        except IOError as e:
            book = catalogue.models.Book.objects.filter(id=book_id, findable=True)
            if not book:
                log.error("Book does not exist for book id = %d" % book_id)
            elif not book.get().children.exists():
                log.error("Cannot open snippet file for book id = %d [rev=%s], %s" % (book_id, revision, e))
            return []
        finally:
            snippets.close()

        # remove verse end markers..
        snips = [s.replace("/\n", "\n") if s else s for s in snips]

        searchresult.snippets = snips

        return snips

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
