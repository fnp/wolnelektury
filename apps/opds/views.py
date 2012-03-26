# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os.path
from urlparse import urljoin

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings
from django.http import Http404
from django.contrib.sites.models import Site

from basicauth import logged_in_or_basicauth, factory_decorator
from catalogue.models import Book, Tag

from search import Search, SearchResult, JVM
from lucene import Term, QueryWrapperFilter, TermQuery

import re

from stats.utils import piwik_track

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


def full_url(url):
    return urljoin("http://%s" % Site.objects.get_current().domain, url)


class OPDSFeed(Atom1Feed):
    link_rel = u"subsection"
    link_type = u"application/atom+xml"

    _book_parent_img = full_url(os.path.join(settings.STATIC_URL, "img/book-parent.png"))
    try:
        _book_parent_img_size = unicode(os.path.getsize(os.path.join(settings.STATIC_ROOT, "img/book-parent.png")))
    except:
        _book_parent_img_size = ''

    _book_img = full_url(os.path.join(settings.STATIC_URL, "img/book.png"))
    try:
        _book_img_size = unicode(os.path.getsize(os.path.join(settings.STATIC_ROOT, "img/book.png")))
    except:
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
        if item['enclosure'] is None:
            handler.addQuickElement(u"link", u"", {u"href": item['link'], u"rel": u"subsection", u"type": u"application/atom+xml"})
            # add a "green book" icon
            handler.addQuickElement(u"link", '',
                {u"rel": u"http://opds-spec.org/thumbnail",
                 u"href": self._book_parent_img,
                 u"length": self._book_parent_img_size,
                 u"type": u"image/png"})
        if item['pubdate'] is not None:
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
            unique_id = get_tag_uri(item['link'], item['pubdate'])
        handler.addQuickElement(u"id", unique_id)

        # Summary.
        # OPDS needs type=text
        if item['description'] is not None:
            handler.addQuickElement(u"summary", item['description'], {u"type": u"text"})

        # Enclosure as OPDS Acquisition Link
        if item['enclosure'] is not None:
            handler.addQuickElement(u"link", '',
                {u"rel": u"http://opds-spec.org/acquisition",
                 u"href": item['enclosure'].url,
                 u"length": item['enclosure'].length,
                 u"type": item['enclosure'].mime_type})
            # add a "red book" icon
            handler.addQuickElement(u"link", '',
                {u"rel": u"http://opds-spec.org/thumbnail",
                 u"href": self._book_img,
                 u"length": self._book_img_size,
                 u"type": u"image/png"})

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
            return book.tags.filter(category='author')[0].name
        except KeyError:
            return u''

    def item_author_link(self, book):
        try:
            return book.tags.filter(category='author')[0].get_absolute_url()
        except KeyError:
            return u''

    def item_enclosure_url(self, book):
        return full_url(book.epub_file.url) if book.epub_file else None

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
        feed = [feed for feed in _root_feeds if feed['category']==category]
        if feed:
            feed = feed[0]
        else:
            raise Http404

        return feed

    def title(self, feed):
        return feed['title']

    def items(self, feed):
        return Tag.objects.filter(category=feed['category']).exclude(book_count=0)

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
        books = Book.tagged.with_any([tag])
        l_tags = Tag.objects.filter(category='book', slug__in=[book.book_tag_slug() for book in books])
        descendants_keys = [book.pk for book in Book.tagged.with_any(l_tags)]
        if descendants_keys:
            books = books.exclude(pk__in=descendants_keys)

        return books


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
        return Tag.objects.filter(category='set', user=user).exclude(book_count=0)

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        return reverse("opds_user_set", args=[item.slug])

    def item_description(self):
        return u''

# no class decorators in python 2.5
#UserFeed = factory_decorator(logged_in_or_basicauth())(UserFeed)


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

# no class decorators in python 2.5
#UserSetFeed = factory_decorator(logged_in_or_basicauth())(UserSetFeed)


@piwik_track
class SearchFeed(AcquisitionFeed):
    description = u"Wyniki wyszukiwania na stronie WolneLektury.pl"
    title = u"Wyniki wyszukiwania"

    INLINE_QUERY_RE = re.compile(r"(author:(?P<author>[^ ]+)|title:(?P<title>[^ ]+)|categories:(?P<categories>[^ ]+)|description:(?P<description>[^ ]+))")
    
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
        JVM.attachCurrentThread()

        query = request.GET.get('q', '')

        inline_criteria = re.findall(self.INLINE_QUERY_RE, query)
        if inline_criteria:
            def get_criteria(criteria, name, position):
                e = filter(lambda el: el[0][0:len(name)] == name, criteria)
                print e
                if not e:
                    return None
                c = e[0][position]
                print c
                if c[0] == '"' and c[-1] == '"':
                    c = c[1:-1]
                    c = c.replace('+', ' ')
                return c

            #import pdb; pdb.set_trace()
            author = get_criteria(inline_criteria, 'author', 1)
            title = get_criteria(inline_criteria, 'title', 2)
            translator = None
            categories = get_criteria(inline_criteria, 'categories', 3)
            query = get_criteria(inline_criteria, 'description', 4)
        else:
            author = request.GET.get('author', '')
            title = request.GET.get('title', '')
            translator = request.GET.get('translator', '')
            categories = None
            fuzzy = False


        srch = Search()
        hint = srch.hint()

        # Scenario 1: full search terms provided.
        # Use auxiliarry information to narrow it and make it better.
        if query:
            filters = []

            if author:
                print "narrow to author %s" % author
                hint.tags(srch.search_tags(author, filt=srch.term_filter(Term('tag_category', 'author'))))

            if translator:
                print "filter by translator %s" % translator
                filters.append(QueryWrapperFilter(
                    srch.make_phrase(srch.get_tokens(translator, field='translators'),
                                     field='translators')))

            if categories:
                filters.append(QueryWrapperFilter(
                    srch.make_phrase(srch.get_tokens(categories, field="tag_name_pl"),
                                     field='tag_name_pl')))

            flt = srch.chain_filters(filters)
            if title:
                print "hint by book title %s" % title
                q = srch.make_phrase(srch.get_tokens(title, field='title'), field='title')
                hint.books(*srch.search_books(q, filt=flt))

            toks = srch.get_tokens(query)
            print "tokens: %s" % toks
            #            import pdb; pdb.set_trace()
            results = SearchResult.aggregate(srch.search_perfect_book(toks, fuzzy=fuzzy, hint=hint),
                srch.search_perfect_parts(toks, fuzzy=fuzzy, hint=hint),
                srch.search_everywhere(toks, fuzzy=fuzzy, hint=hint))
            results.sort(reverse=True)
            return [r.book for r in results]
        else:
            # Scenario 2: since we no longer have to figure out what the query term means to the user,
            # we can just use filters and not the Hint class.
            filters = []

            fields = {
                'author': author,
                'translators': translator,
                'title': title
                }

            for fld, q in fields.items():
                if q:
                    filters.append(QueryWrapperFilter(
                        srch.make_phrase(srch.get_tokens(q, field=fld), field=fld)))

            flt = srch.chain_filters(filters)
            books = srch.search_books(TermQuery(Term('is_book', 'true')), filt=flt)
            return books

    def get_link(self, query):
        return "%s?q=%s" % (reverse('search'), query)

    def items(self, books):
        try:
            return books
        except ValueError:
            # too short a query
            return []
