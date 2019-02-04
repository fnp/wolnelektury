# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from piston.authentication import OAuthAuthentication, oauth_access_token, oauth_request_token
from piston.resource import Resource
import catalogue.views
from api import handlers
from api.helpers import CsrfExemptResource
from api.piston_patch import oauth_user_auth
from . import views

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
filter_book_resource = auth_resource(handler=handlers.FilterBooksHandler)

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

    # reading data
    url(r'^reading/(?P<slug>[a-z0-9-]+)/$', views.BookUserDataView.as_view(), name='api_reading'),
    url(r'^reading/(?P<slug>[a-z0-9-]+)/(?P<state>[a-z]+)/$', views.BookUserDataView.as_view(), name='api_reading'),
    url(r'^username/$', views.UserView.as_view(), name='api_username'),

    # books by tags
    url(tags_re + r'ebooks/' + paginate_re,
        ebook_list_resource, name='api_ebook_list'),
    url(tags_re + r'parent_ebooks/' + paginate_re,
        ebook_list_resource, {"top_level": True}, name='api_parent_ebook_list'),

    url(r'^filter-books/$', filter_book_resource, name='api_filter_books'),

    url(r'^pictures/$', picture_resource),

    url(r'^blog/$', blog_resource),

    url(r'^', include('social.api.urls')),
    url(r'^', include('catalogue.api.urls')),
]
