# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from piston.authentication import OAuthAuthentication, oauth_access_token, oauth_request_token
from piston.resource import Resource
import catalogue.views
from api import handlers
from api.helpers import CsrfExemptResource
from api.piston_patch import oauth_user_auth

auth = OAuthAuthentication(realm="Wolne Lektury")


class DjangoAuthentication(object):
    """
    Authentication handler that always returns
    True, so no authentication is needed, nor
    initiated (`challenge` is missing.)
    """
    def is_authenticated(self, request):
        return request.user.is_authenticated()

    def challenge(self):
        from django.http import HttpResponse
        resp = HttpResponse("Authorization Required")
        resp.status_code = 401
        return resp


def auth_resource(handler):
    from django.conf import settings
    if settings.DEBUG:
        django_auth = DjangoAuthentication()
        return CsrfExemptResource(handler=handler, authentication=django_auth)
    return CsrfExemptResource(handler=handler, authentication=auth)


book_list_resource = auth_resource(handler=handlers.BooksHandler)
ebook_list_resource = Resource(handler=handlers.EBooksHandler)
# book_list_resource = Resource(handler=handlers.BooksHandler)
book_resource = Resource(handler=handlers.BookDetailHandler)
filter_book_resource = auth_resource(handler=handlers.FilterBooksHandler)
epub_resource = auth_resource(handler=handlers.EpubHandler)

preview_resource = Resource(handler=handlers.BookPreviewHandler)

reading_resource = auth_resource(handler=handlers.UserDataHandler)
shelf_resource = auth_resource(handler=handlers.UserShelfHandler)

like_resource = auth_resource(handler=handlers.UserLikeHandler)

collection_resource = Resource(handler=handlers.CollectionDetailHandler)
collection_list_resource = Resource(handler=handlers.CollectionsHandler)

tag_list_resource = Resource(handler=handlers.TagsHandler)
tag_resource = Resource(handler=handlers.TagDetailHandler)

fragment_resource = Resource(handler=handlers.FragmentDetailHandler)
fragment_list_resource = Resource(handler=handlers.FragmentsHandler)

picture_resource = auth_resource(handler=handlers.PictureHandler)

blog_resource = Resource(handler=handlers.BlogEntryHandler)


tags_re = r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){0,6})'
paginate_re = r'(?:after/(?P<after>[a-z0-9-]+)/)?(?:count/(?P<count>[0-9]+)/)?$'


urlpatterns = [
    url(r'^oauth/request_token/$', oauth_request_token),
    url(r'^oauth/authorize/$', oauth_user_auth, name='oauth_user_auth'),
    url(r'^oauth/access_token/$', csrf_exempt(oauth_access_token)),

    url(r'^$', TemplateView.as_view(template_name='api/main.html'), name='api'),

    # info boxes (used by mobile app)
    url(r'book/(?P<book_id>\d*?)/info\.html$', catalogue.views.book_info),
    url(r'tag/(?P<tag_id>\d*?)/info\.html$', catalogue.views.tag_info),

    # books by collections
    url(r'^collections/$', collection_list_resource, name="api_collections"),
    url(r'^collections/(?P<slug>[^/]+)/$', collection_resource, name="api_collection"),

    # epub preview
    url(r'^epub/(?P<slug>[a-z0-9-]+)/$', epub_resource, name='api_epub'),

    # reading data
    url(r'^reading/(?P<slug>[a-z0-9-]+)/$', reading_resource, name='api_reading'),
    url(r'^reading/(?P<slug>[a-z0-9-]+)/(?P<state>[a-z]+)/$', reading_resource, name='api_reading'),
    url(r'^shelf/(?P<state>[a-z]+)/$', shelf_resource, name='api_shelf'),
    url(r'^username/$', reading_resource, name='api_username'),

    url(r'^like/(?P<slug>[a-z0-9-]+)/$', like_resource, name='api_like'),

    # objects details
    url(r'^books/(?P<book>[a-z0-9-]+)/$', book_resource, name="api_book"),
    url(r'^(?P<category>[a-z0-9-]+)/(?P<slug>[a-z0-9-]+)/$',
        tag_resource, name="api_tag"),
    url(r'^books/(?P<book>[a-z0-9-]+)/fragments/(?P<anchor>[a-z0-9-]+)/$',
        fragment_resource, name="api_fragment"),

    # books by tags
    url(tags_re + r'books/' + paginate_re,
        book_list_resource, name='api_book_list'),
    url(tags_re + r'ebooks/' + paginate_re,
        ebook_list_resource, name='api_ebook_list'),
    url(tags_re + r'parent_books/' + paginate_re,
        book_list_resource, {"top_level": True}, name='api_parent_book_list'),
    url(tags_re + r'parent_ebooks/' + paginate_re,
        ebook_list_resource, {"top_level": True}, name='api_parent_ebook_list'),
    url(tags_re + r'audiobooks/' + paginate_re,
        book_list_resource, {"audiobooks": True}, name='api_audiobook_list'),
    url(tags_re + r'daisy/' + paginate_re,
        book_list_resource, {"daisy": True}, name='api_daisy_list'),

    url(r'^recommended/' + paginate_re, book_list_resource, {"recommended": True}, name='api_recommended_list'),
    url(r'^newest/$', book_list_resource, {"newest": True, "top_level": True, "count": 20}, name='api_newest_list'),
    url(r'^filter-books/$', filter_book_resource, name='api_filter_books'),

    url(r'^preview/$', preview_resource, name='api_preview'),

    url(r'^pictures/$', picture_resource),

    url(r'^blog/$', blog_resource),

    # fragments by book, tags, themes
    # this should be paged
    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){1,6})fragments/$', fragment_list_resource),

    # tags by category
    url(r'^(?P<category>[a-z0-9-]+)/$', tag_list_resource, name='api_tag_list'),
]
