# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from piston.authentication import OAuthAuthentication, oauth_access_token
from piston.resource import Resource
from ssify import ssi_included
from api import handlers
from api.helpers import CsrfExemptResource

auth = OAuthAuthentication(realm="Wolne Lektury")

book_list_resource = CsrfExemptResource(handler=handlers.BooksHandler, authentication=auth)
ebook_list_resource = Resource(handler=handlers.EBooksHandler)
# book_list_resource = Resource(handler=handlers.BooksHandler)
book_resource = Resource(handler=handlers.BookDetailHandler)
filter_book_resource = Resource(handler=handlers.FilterBooksHandler)

collection_resource = Resource(handler=handlers.CollectionDetailHandler)
collection_list_resource = Resource(handler=handlers.CollectionsHandler)

tag_list_resource = Resource(handler=handlers.TagsHandler)
tag_resource = Resource(handler=handlers.TagDetailHandler)

fragment_resource = Resource(handler=handlers.FragmentDetailHandler)
fragment_list_resource = Resource(handler=handlers.FragmentsHandler)

picture_resource = CsrfExemptResource(handler=handlers.PictureHandler, authentication=auth)


tags_re = r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){0,6})'
paginate_re = r'(?:before/(?P<before>[a-z0-9-]+)/)?(?:after/(?P<after>[a-z0-9-]+)/)?(?:count/(?P<count>[0-9]+)/)?$'


@ssi_included
def incl(request, model, pk, emitter_format):
    resource = {
        'book': book_list_resource,
        'fragment': fragment_list_resource,
        'tag': tag_list_resource,
        }[model]
    request.piwik_track = False
    resp = resource(request, pk=pk, emitter_format=emitter_format)
    if emitter_format == 'xml':
        # Ugly, but quick way of stripping <?xml?> header and <response> tags.
        resp.content = resp.content[49:-11]
    return resp


urlpatterns = patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$', 'oauth_request_token'),
    url(r'^oauth/authorize/$', 'oauth_user_auth'),
    url(r'^oauth/access_token/$', csrf_exempt(oauth_access_token)),

) + patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='api/main.html'), name='api'),
    url(r'^include/(?P<model>book|fragment|tag)/(?P<pk>\d+)\.(?P<lang>.+)\.(?P<emitter_format>xml|json)$',
        incl, name='api_include'),

    # info boxes (used by mobile app)
    url(r'book/(?P<book_id>\d*?)/info\.html$', 'catalogue.views.book_info'),
    url(r'tag/(?P<tag_id>\d*?)/info\.html$', 'catalogue.views.tag_info'),

    # books by collections
    url(r'^collections/$', collection_list_resource, name="api_collections"),
    url(r'^collections/(?P<slug>[^/]+)/$', collection_resource, name="api_collection"),

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
    url(r'^newest/', book_list_resource, {"newest": True, "count": 20}, name='api_newest_list'),
    url(r'^filter-books/(?:title-part/(?P<title_part>[^/]+)/)?(?:author-part/(?P<author_part>[^/]+)/)?'
        r'(?:lektura/(?P<is_lektura>(?:true|false))/)?(?:audiobook/(?P<is_audiobook>(?:true|false))/)?'
        + paginate_re, filter_book_resource, name='api_filter_books'),

    url(r'^pictures/$', picture_resource),

    # fragments by book, tags, themes
    # this should be paged
    url(r'^(?P<tags>(?:(?:[a-z0-9-]+/){2}){1,6})fragments/$', fragment_list_resource),

    # tags by category
    url(r'^(?P<category>[a-z0-9-]+)/$', tag_list_resource, name='api_tag_list'),
)
