from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.ClubView.as_view()),
    url(r'^dolacz/$', views.JoinView.as_view(), name='club_join'),
    url(r'^dolacz/app/$', views.AppJoinView.as_view(), name='club_join'),

    url(r'^plan/(?P<key>[-a-z0-9]+)/$', views.ScheduleView.as_view(), name='club_schedule'),
    url(r'^przylacz/(?P<key>[-a-z0-9]+)/$', views.claim, name='club_claim'),
    url(r'^anuluj/(?P<key>[-a-z0-9]+)/$', views.cancel, name='club_cancel'),

    url(r'^testowa-platnosc/(?P<key>[-a-z0-9]+)/$', views.DummyPaymentView.as_view(), name='club_dummy_payment'),
]
