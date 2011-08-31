# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource

from api import handlers


book_changes_resource = Resource(handler=handlers.BookChangesHandler)
tag_changes_resource = Resource(handler=handlers.TagChangesHandler)
changes_resource = Resource(handler=handlers.ChangesHandler)

urlpatterns = patterns('',
    url(r'^book_changes/(?P<since>\d*?)\.(?P<emitter_format>xml|json|yaml)$', book_changes_resource),
    url(r'^tag_changes/(?P<since>\d*?)\.(?P<emitter_format>xml|json|yaml)$', tag_changes_resource),
    url(r'^changes/(?P<since>\d*?)\.(?P<emitter_format>xml|json|yaml)$', changes_resource),


    url(r'book/(?P<id>\d*?)/info\.html$', 'catalogue.views.book_info'),
    url(r'tag/(?P<id>\d*?)/info\.html$', 'catalogue.views.tag_info'),
)
