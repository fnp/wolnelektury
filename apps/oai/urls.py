
from django.conf.urls.defaults import *

urlpatterns = patterns('oai.views',
                       url(r'^$', 'oaipmh', name='oaipmh'))
