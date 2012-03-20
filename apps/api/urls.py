# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.authentication import OAuthAuthentication
from piston.resource import Resource

from api import handlers
from catalogue.models import Book

auth = OAuthAuthentication(realm="Wolne Lektury")

book_changes_resource = Resource(handler=handlers.BookChangesHandler)
tag_changes_resource = Resource(handler=handlers.TagChangesHandler)
changes_resource = Resource(handler=handlers.ChangesHandler)

book_list_resource = Resource(handler=handlers.BooksHandler, authentication=auth)
#book_list_resource = Resource(handler=handlers.BooksHandler)
book_resource = Resource(handler=handlers.BookDetailHandler)

tag_list_resource = Resource(handler=handlers.TagsHandler)
tag_resource = Resource(handler=handlers.TagDetailHandler)

fragment_resource = Resource(handler=handlers.FragmentDetailHandler)
fragment_list_resource = Resource(handler=handlers.FragmentsHandler)

picture_resource = Resource(handler=handlers.PictureHandler, authentication=auth)

urlpatterns = patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$', 'oauth_request_token'),
    url(r'^oauth/authorize/$', 'oauth_user_auth'),
    url(r'^oauth/access_token/$', 'oauth_access_token'),

) + patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template',
            {'template': 'api/main.html'}, name='api'),


    # changes handlers
    url(r'^book_changes/(?P<since>\d*?)\.(?P<emitter_format>xml|json|yaml)$', book_changes_resource),
    url(r'^tag_changes/(?P<since>\d*?)\.(?P<emitter_format>xml|json|yaml)$', tag_changes_resource),
    # used by mobile app
    url(r'^changes/(?P<since>\d*?)\.(?P<emitter_format>xml|json|yaml)$', changes_resource),

    # info boxes (used by mobile app)
    url(r'book/(?P<id>\d*?)/info\.html$', 'catalogue.views.book_info'),
    url(r'tag/(?P<id>\d*?)/info\.html$', 'catalogue.views.tag_info'),


    # objects details
    url(r'^books/(?P<book>[a-z0-9-]+)/$', book_resource, name="api_book"),
    url(r'^(?P<category>[a-z0-9-]+)/(?P<slug>[a-z0-9-]+)/$',
        tag_resource, name="api_tag"),
    url(r'^books/(?P<book>[a-z0-9-]+)/fragments/(?P<anchor>[a-z0-9-]+)/$',
        fragment_resource, name="api_fragment"),

    # books by tags
    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){0,6})books/$', book_list_resource),
    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){0,6})parent_books/$', book_list_resource, {"top_level": True}),

    url(r'^pictures/$', picture_resource),

    # fragments by book, tags, themes
    # this should be paged
    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){1,6})fragments/$', fragment_list_resource),

    # tags by category
    url(r'^(?P<category>[a-z0-9-]+)/$', tag_list_resource),
)
