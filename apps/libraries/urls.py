from django.conf.urls.defaults import patterns, url
from django.http import HttpResponseRedirect


urlpatterns = patterns('libraries.views',
    url(r'^$', 'main_view', name='libraries_main_view'),
    url(r'^/$', lambda x: HttpResponseRedirect(x.path[:-1])),
    url(r'^/(?P<slug>[a-zA-Z0-9_-]+)$', 'catalog_view', name='libraries_catalog_view'),
)