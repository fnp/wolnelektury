# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import OAuthAuthentication

from api.handlers import BookHandler, TagHandler


auth = OAuthAuthentication(realm='API')
book_resource = Resource(handler=BookHandler)
tag_resource = Resource(handler=TagHandler, authentication=auth)

urlpatterns = patterns('',
    url(r'^books/(?P<slug>[^/]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource),
    url(r'^books\.(?P<emitter_format>xml|json|yaml)$', book_resource),
    url(r'^tags/(?P<tags>[a-zA-Z0-9-/]*)\.(?P<emitter_format>xml|json|yaml)$', tag_resource),
    url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource), #detail
    url(r'^lektura/(?P<book_slug>[a-zA-Z0-9-]+)/motyw/(?P<theme_slug>[a-zA-Z0-9-]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource), #fragments
    url(r'^oauth/callback/$','oauth_callback'),
)

urlpatterns += patterns(
'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)