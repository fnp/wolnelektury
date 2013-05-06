from django.conf.urls.defaults import *


urlpatterns = patterns('libraries.views',
    url(r'^$', 'main_view', name='libraries_main_view'),
)