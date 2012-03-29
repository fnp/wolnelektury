from django.conf.urls.defaults import *

urlpatterns = patterns('waiter.views',
    url(r'^(?P<path>.*)$', 'wait', name='waiter'),
)
