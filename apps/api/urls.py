# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource
#from piston.authentication import HttpBasicAuthentication

#from api.handlers import BookHandler, TagHandler
from api import handlers


#auth = OAuthAuthentication(realm='API')
#book_changes_resource = Resource(handler=handlers.BookChangesHandler)
#tag_changes_resource = Resource(handler=handlers.TagChangesHandler)#, authentication=auth)
changes_resource = Resource(handler=handlers.ChangesHandler)

urlpatterns = patterns('',
    #url(r'^book_changes/(?P<since>\d*(\.\d*)?)\.(?P<emitter_format>xml|json|yaml)$', book_changes_resource),
    #url(r'^tag_changes/(?P<since>\d*(\.\d*)?)\.(?P<emitter_format>xml|json|yaml)$', tag_changes_resource),
    url(r'^changes/(?P<since>\d*(\.\d*)?)\.(?P<emitter_format>xml|json|yaml)$', changes_resource),

    #url(r'^books/(?P<id>[\d,]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource),
    #url(r'^books\.(?P<emitter_format>xml|json|yaml)$', book_resource),

    #url(r'^tags/(?P<tags>[a-zA-Z0-9-/]*)\.(?P<emitter_format>xml|json|yaml)$', tag_resource),
    #url(r'^lektura/(?P<slug>[a-zA-Z0-9-]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource), #detail
    #url(r'^lektura/(?P<book_slug>[a-zA-Z0-9-]+)/motyw/(?P<theme_slug>[a-zA-Z0-9-]+)\.(?P<emitter_format>xml|json|yaml)$', book_resource), #fragments
    #url(r'^oauth/callback/$','oauth_callback'),
)

"""
urlpatterns += patterns(
'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)
"""
