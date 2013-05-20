from django.conf.urls import patterns, url, include


urlpatterns = patterns('polls.views',
    url(r'^(?P<slug>[^/]+)$', 'poll', name='poll'),
)
