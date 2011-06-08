# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import OAuthAuthentication

from api.handlers import BookHandler


auth = OAuthAuthentication(realm="Wolne Lektury")
book_resource = Resource(handler=BookHandler, authentication=auth)


urlpatterns = patterns('',  
    url(r'^books/(?P<slug>[^/]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource),
    url(r'^books\.(?P<emitter_format>xml|json|yaml)$', book_resource),

) + patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)
