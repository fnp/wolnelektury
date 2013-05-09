from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('libraries.views',
    url(r'^(?P<slug>[a-zA-Z0-9_-]+)$', 'main_view', name='libraries_main_view'),
)