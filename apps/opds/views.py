# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from base64 import b64encode
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
from catalogue.views import books_starting_with

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
        return full_url(book.root_ancestor.epub_file.url)

    def item_enclosure_length(self, book):
        return book.root_ancestor.epub_file.size

@piwik_track
class RootFeed(Feed):
    feed_type = OPDSFeed
    title = u'Wolne Lektury'
    link = u'http://www.wolnelektury.pl/'
    description = u"Spis utworów na stronie http://WolneLektury.pl"
    author_name = u"Wolne Lektury"
    author_link = u"http://www.wolnelektury.pl/"

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
    link = u'http://www.wolnelektury.pl/'
    description = u"Spis utworów na stronie http://WolneLektury.pl"
    author_name = u"Wolne Lektury"
    author_link = u"http://www.wolnelektury.pl/"

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
    author_link = u"http://www.wolnelektury.pl/"

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
    
    def get_object(self, request):
        return request.GET.get('q', '')

    def get_link(self, query):
        return "%s?q=%s" % (reverse('search'), query) 

    def items(self, query):
        try:
            return books_starting_with(query)
        except ValueError:
            # too short a query
            return []
