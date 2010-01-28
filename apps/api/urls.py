# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from api.handlers import BookHandler


auth = HttpBasicAuthentication(realm='My sample API')
book_resource = Resource(handler=BookHandler, authentication=auth)


urlpatterns = patterns('',
    url(r'^books/(?P<slug>[^/]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource),
    url(r'^books\.(?P<emitter_format>xml|json|yaml)$', book_resource),
)

