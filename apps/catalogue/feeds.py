# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#

#############################################################################
# from: http://djangosnippets.org/snippets/243/

import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate, login

#
def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
    This is a helper function used by 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' (deleted) that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response
    

#
def logged_in_or_basicauth(realm = ""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated(),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator


#############################################################################


from base64 import b64encode
import os.path

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings
from django.http import Http404
from django.contrib.sites.models import Site

from catalogue.models import Book, Tag


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


def factory_decorator(decorator):
    """ generates a decorator for a function factory class
    if A(*) == f, factory_decorator(D)(A)(*) == D(f)
    """
    def fac_dec(func):
        def wrapper(*args, **kwargs):
            return decorator(func(*args, **kwargs))
        return wrapper
    return fac_dec


class OPDSFeed(Atom1Feed):
    link_rel = u"subsection"
    link_type = u"application/atom+xml"

    _book_parent_img = "http://%s%s" % (Site.objects.get_current().domain, os.path.join(settings.STATIC_URL, "img/book-parent.png"))
    try:
        _book_parent_img_size = unicode(os.path.getsize(os.path.join(settings.STATIC_ROOT, "img/book-parent.png")))
    except:
        _book_parent_img_size = ''

    _book_img = "http://%s%s" % (Site.objects.get_current().domain, os.path.join(settings.STATIC_URL, "img/book.png"))
    try:
        _book_img_size = unicode(os.path.getsize(os.path.join(settings.STATIC_ROOT, "img/book.png")))
    except:
        _book_img_size = ''

    def add_root_elements(self, handler):
        super(OPDSFeed, self).add_root_elements(handler)
        handler.addQuickElement(u"link", u"", {u"href": reverse("opds_authors"), u"rel": u"start", u"type": u"application/atom+xml"})


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
        return (tag for tag in Tag.objects.filter(category=feed['category']) if tag.get_count() > 0)

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        return reverse("opds_by_tag", args=[item.category, item.slug])

    def item_description(self):
        return u''


class ByTagFeed(Feed):
    feed_type = OPDSFeed
    link = u'http://www.wolnelektury.pl/'
    item_enclosure_mime_type = "application/epub+zip"
    author_name = u"Wolne Lektury"
    author_link = u"http://www.wolnelektury.pl/"

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
        return "http://%s%s" % (Site.objects.get_current().domain, book.root_ancestor.epub_file.url)

    def item_enclosure_length(self, book):
        return book.root_ancestor.epub_file.size


@factory_decorator(logged_in_or_basicauth())
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
        return (tag for tag in Tag.objects.filter(category='set', user=user) if tag.get_count() > 0)

    def item_title(self, item):
        return item.name

    def item_link(self, item):
        return reverse("opds_user_set", args=[item.slug])

    def item_description(self):
        return u''


@factory_decorator(logged_in_or_basicauth())
class UserSetFeed(Feed):
    feed_type = OPDSFeed
    link = u'http://www.wolnelektury.pl/'
    item_enclosure_mime_type = "application/epub+zip"
    author_name = u"Wolne Lektury"
    author_link = u"http://www.wolnelektury.pl/"

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
        return "http://%s%s" % (Site.objects.get_current().domain, book.root_ancestor.epub_file.url)

    def item_enclosure_length(self, book):
        return book.root_ancestor.epub_file.size

@logged_in_or_basicauth()
def user_set_feed(request):
    return UserSetFeed()(request)

