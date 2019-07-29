# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from functools import reduce
import os.path
from urllib.parse import urljoin

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings
from django.http import Http404
from django.contrib.sites.models import Site
from django.utils.functional import lazy

from basicauth import logged_in_or_basicauth, factory_decorator
from catalogue.models import Book, Tag

from search.views import Search
import operator
import logging
import re

from stats.utils import piwik_track

log = logging.getLogger('opds')

_root_feeds = (
    {
        u"category": u"",
        u"link": u"opds_user",
        u"link_args": [],
        u"title": u"Moje półki",
        u"description": u"Półki użytkownika dostępne po zalogowaniu"
    },
    {
        u"category": u"author",
        u"link": u"opds_by_category",
        u"link_args": [u"author"],
        u"title": u"Autorzy",
        u"description": u"Utwory wg autorów"
    },
    {
        u"category": u"kind",
        u"link": u"opds_by_category",
        u"link_args": [u"kind"],
        u"title": u"Rodzaje",
        u"description": u"Utwory wg rodzajów"
    },
    {
        u"category": u"genre",
        u"link": u"opds_by_category",
        u"link_args": [u"genre"],
        u"title": u"Gatunki",
        u"description": u"Utwory wg gatunków"
    },
    {
        u"category": u"epoch",
        u"link": u"opds_by_category",
        u"link_args": [u"epoch"],
        u"title": u"Epoki",
        u"description": u"Utwory wg epok"
    },
)


current_domain = lazy(lambda: Site.objects.get_current().domain, str)()


def full_url(url):
    return urljoin("http://%s" % current_domain, url)


class OPDSFeed(Atom1Feed):
    link_rel = u"subsection"
    link_type = u"application/atom+xml"

    _book_parent_img = lazy(lambda: full_url(os.path.join(settings.STATIC_URL, "img/book-parent.png")), str)()
    try:
        _book_parent_img_size = str(os.path.getsize(os.path.join(settings.STATIC_ROOT, "img/book-parent.png")))
    except OSError:
        _book_parent_img_size = ''

    _book_img = lazy(lambda: full_url(os.path.join(settings.STATIC_URL, "img/book.png")), str)()
    try:
        _book_img_size = str(os.path.getsize(os.path.join(settings.STATIC_ROOT, "img/book.png")))
    except OSError:
        _book_img_size = ''

    def add_root_elements(self, handler):
        super(OPDSFeed, self).add_root_elements(handler)
        handler.addQuickElement(u"link", None,
                                {u"href": reverse("opds_authors"),
                                 u"rel": u"start",
                                 u"type": u"application/atom+xml"})
        handler.addQuickElement(u"link", None,
                                {u"href": full_url(os.path.join(settings.STATIC_URL, "opensearch.xml")),
                                 u"rel": u"search",
                                 u"type": u"application/opensearchdescription+xml"})

    def add_item_elements(self, handler, item):
        """ modified from Atom1Feed.add_item_elements """
        handler.addQuickElement(u"title", item['title'])

        # add a OPDS Navigation link if there's no enclosure
        if not item.get('enclosures') is None:
            handler.addQuickElement(
                u"link", u"", {u"href": item['link'], u"rel": u"subsection", u"type": u"application/atom+xml"})
            # add a "green book" icon
            handler.addQuickElement(
                u"link", '',
                {
                    u"rel": u"http://opds-spec.org/thumbnail",
                    u"href": self._book_parent_img,
                    u"length": self._book_parent_img_size,
                    u"type": u"image/png",
                })
        if item['pubdate'] is not None:
            # FIXME: rfc3339_date is undefined, is this ever run?
            handler.addQuickElement(u"updated", rfc3339_date(item['pubdate']).decode('utf-8'))

        # Author information.
        if item['author_name'] is not None:
            handler.startElement(u"author", {})
            handler.addQuickElement(u"name", item['author_name'])
            if item['author_email'] is not None:
                handler.addQuickElement(u"email", item['author_email'])
            if item['author_link'] is not None:
                handler.addQuickElement(u"uri", item['author_link'])
            handler.endElement(u"author")

        # Unique ID.
        if item['unique_id'] is not None:
            unique_id = item['unique_id']
        else:
            # FIXME: get_tag_uri is undefined, is this ever run?
            unique_id = get_tag_uri(item['link'], item['pubdate'])
        handler.addQuickElement(u"id", unique_id)

        # Summary.
        # OPDS needs type=text
        if item['description'] is not None:
            handler.addQuickElement(u"summary", item['description'], {u"type": u"text"})

        # Enclosure as OPDS Acquisition Link
        for enc in item.get('enclosures', []):
            handler.addQuickElement(
                u"link", '',
                {
                    u"rel": u"http://opds-spec.org/acquisition",
                    u"href": enc.url,
                    u"length": enc.length,
                    u"type": enc.mime_type,
                })
            # add a "red book" icon
            handler.addQuickElement(
                u"link", '',
                {
                    u"rel": u"http://opds-spec.org/thumbnail",
                    u"href": self._book_img,
                    u"length": self._book_img_size,
                    u"type": u"image/png",
                })

        # Categories.
        for cat in item['categories']:
            handler.addQuickElement(u"category", u"", {u"term": cat})

        # Rights.
        if item['item_copyright'] is not None:
            handler.addQuickElement(u"rights", item['item_copyright'])


class AcquisitionFeed(Feed):
    feed_type = OPDSFeed
    link = u'http://www.wolnelektury.pl/'
    item_enclosure_mime_type = "application/epub+zip"
    author_name = u"Wolne Lektury"
    author_link = u"http://www.wolnelektury.pl/"

    def item_title(self, book):
        return book.title

    def item_description(self):
        return u''

    def item_link(self, book):
        return book.get_absolute_url()

    def item_author_name(self, book):
        try:
            return book.authors().first().name
        except AttributeError:
            return u''

    def item_author_link(self, book):
        try:
            return book.authors().first().get_absolute_url()
        except AttributeError:
            return u''

    def item_enclosure_url(self, book):
        return full_url(book.epub_url()) if book.epub_file else None

    def item_enclosure_length(self, book):
        return book.epub_file.size if book.epub_file else None


@piwik_track
class RootFeed(Feed):
    feed_type = OPDSFeed
    title = u'Wolne Lektury'
    link = u'http://wolnelektury.pl/'
    description = u"Spis utworów na stronie http://WolneLektury.pl"
    author_name = u"Wolne Lektury"
    author_link = u"http://wolnelektury.pl/"

    def items(self):
        return _root_feeds

    def item_title(self, item):
        return item['title']

    def item_link(self, item):
        return reverse(item['link'], args=item['link_args'])

    def item_description(self, item):
        return item['description']


@piwik_track
class ByCategoryFeed(Feed):
    feed_type = OPDSFeed
    link = u'http://wolnelektury.pl/'
    description = u"Spis utworów na stronie http://WolneLektury.pl"
    author_name = u"Wolne Lektury"
    author_link = u"http://wolnelektury.pl/"

    def get_object(self, request, category):
        feed = [feed for feed in _root_feeds if feed['category'] == category]
        if feed:
            feed = feed[0]
        else:
            raise Http404

        return feed

    def title(self, feed):
        return feed['title']

    def items(self, feed):
        return Tag.objects.filter(category=feed['category']).exclude(items=None)

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        return reverse("opds_by_tag", args=[item.category, item.slug])

    def item_description(self):
        return u''


@piwik_track
class ByTagFeed(AcquisitionFeed):
    def link(self, tag):
        return tag.get_absolute_url()

    def title(self, tag):
        return tag.name

    def description(self, tag):
        return u"Spis utworów na stronie http://WolneLektury.pl"

    def get_object(self, request, category, slug):
        return get_object_or_404(Tag, category=category, slug=slug)

    def items(self, tag):
        return Book.tagged_top_level([tag])


@factory_decorator(logged_in_or_basicauth())
@piwik_track
class UserFeed(Feed):
    feed_type = OPDSFeed
    link = u'http://www.wolnelektury.pl/'
    description = u"Półki użytkownika na stronie http://WolneLektury.pl"
    author_name = u"Wolne Lektury"
    author_link = u"http://wolnelektury.pl/"

    def get_object(self, request):
        return request.user

    def title(self, user):
        return u"Półki użytkownika %s" % user.username

    def items(self, user):
        return Tag.objects.filter(category='set', user=user).exclude(items=None)

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        return reverse("opds_user_set", args=[item.slug])

    def item_description(self):
        return u''


@factory_decorator(logged_in_or_basicauth())
@piwik_track
class UserSetFeed(AcquisitionFeed):
    def link(self, tag):
        return tag.get_absolute_url()

    def title(self, tag):
        return tag.name

    def description(self, tag):
        return u"Spis utworów na stronie http://WolneLektury.pl"

    def get_object(self, request, slug):
        return get_object_or_404(Tag, category='set', slug=slug, user=request.user)

    def items(self, tag):
        return Book.tagged.with_any([tag])


@piwik_track
class SearchFeed(AcquisitionFeed):
    description = u"Wyniki wyszukiwania na stronie WolneLektury.pl"
    title = u"Wyniki wyszukiwania"

    QUOTE_OR_NOT = r'(?:(?=["])"([^"]+)"|([^ ]+))'
    INLINE_QUERY_RE = re.compile(
        r"author:" + QUOTE_OR_NOT +
        "|translator:" + QUOTE_OR_NOT +
        "|title:" + QUOTE_OR_NOT +
        "|categories:" + QUOTE_OR_NOT +
        "|description:" + QUOTE_OR_NOT +
        "|text:" + QUOTE_OR_NOT
        )
    MATCHES = {
        'author': (0, 1),
        'translator': (2, 3),
        'title': (4, 5),
        'categories': (6, 7),
        'description': (8, 9),
        'text': (10, 11),
        }

    PARAMS_TO_FIELDS = {
        'author': 'authors',
        'translator': 'translators',
        #        'title': 'title',
        'categories': 'tag_name_pl',
        'description': 'text',
        #        'text': 'text',
        }

    ATOM_PLACEHOLDER = re.compile(r"^{(atom|opds):\w+}$")

    def get_object(self, request):
        """
        For OPDS 1.1 We should handle a query for search terms
        and criteria provided either as opensearch or 'inline' query.
        OpenSearch defines fields: atom:author, atom:contributor (treated as translator),
        atom:title. Inline query provides author, title, categories (treated as book tags),
        description (treated as content search terms).

        if search terms are provided, we shall search for books
        according to Hint information (from author & contributror & title).

        but if search terms are empty, we should do a different search
        (perhaps for is_book=True)

        """

        query = request.GET.get('q', '')

        inline_criteria = re.findall(self.INLINE_QUERY_RE, query)
        if inline_criteria:
            remains = re.sub(self.INLINE_QUERY_RE, '', query)
            remains = re.sub(r'[ \t]+', ' ', remains)

            def get_criteria(criteria, name):
                for c in criteria:
                    for p in self.MATCHES[name]:
                        if c[p]:
                            if p % 2 == 0:
                                return c[p].replace('+', ' ')
                            return c[p]
                return None

            criteria = dict(map(
                lambda cn: (cn, get_criteria(inline_criteria, cn)),
                ['author', 'translator', 'title', 'categories',
                 'description', 'text']))
            query = remains
            # empty query and text set case?
            log.debug("Inline query = [%s], criteria: %s" % (query, criteria))
        else:
            def remove_dump_data(val):
                """Some clients don't get opds placeholders and just send them."""
                if self.ATOM_PLACEHOLDER.match(val):
                    return ''
                return val

            criteria = dict(
                (cn, remove_dump_data(request.GET.get(cn, '')))
                for cn in self.MATCHES.keys())
            # query is set above.
            log.debug("Inline query = [%s], criteria: %s" % (query, criteria))

        srch = Search()

        book_hit_filter = srch.index.Q(book_id__any=True)
        filters = [book_hit_filter] + [srch.index.Q(
            **{self.PARAMS_TO_FIELDS.get(cn, cn): criteria[cn]}
            ) for cn in self.MATCHES.keys() if cn in criteria
            if criteria[cn]]

        if query:
            q = srch.index.query(
                reduce(
                    operator.or_,
                    [srch.index.Q(**{self.PARAMS_TO_FIELDS.get(cn, cn): query}) for cn in self.MATCHES.keys()],
                    srch.index.Q()))
        else:
            q = srch.index.query(srch.index.Q())

        q = srch.apply_filters(q, filters).field_limit(score=True, fields=['book_id'])
        results = q.execute()

        book_scores = dict([(r['book_id'], r['score']) for r in results])
        books = Book.objects.filter(id__in=set([r['book_id'] for r in results]))
        books = list(books)
        books.sort(reverse=True, key=lambda book: book_scores[book.id])
        return books

    def get_link(self, query):
        return "%s?q=%s" % (reverse('search'), query)

    def items(self, books):
        try:
            return books
        except ValueError:
            # too short a query
            return []
