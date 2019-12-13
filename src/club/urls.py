# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from annoy.utils import banner_exempt
from . import views


urlpatterns = [
    url(r'^$', banner_exempt(views.JoinView.as_view()), name='club_join'),
    url(r'^info/$', banner_exempt(views.ClubView.as_view()), name='club'),

    url(r'^plan/(?P<key>[-a-z0-9]+)/$', banner_exempt(views.ScheduleView.as_view()), name='club_schedule'),
    url(r'^plan/(?P<key>[-a-z0-9]+)/dziekujemy/$', banner_exempt(views.ScheduleThanksView.as_view()), name='club_thanks'),

    url(r'^przylacz/(?P<key>[-a-z0-9]+)/$', views.claim, name='club_claim'),
    url(r'^anuluj/(?P<key>[-a-z0-9]+)/$', views.cancel, name='club_cancel'),
    url(r'^testowa-platnosc/(?P<key>[-a-z0-9]+)/$', views.DummyPaymentView.as_view(), name='club_dummy_payment'),

    url(r'platnosc/payu/cykl/(?P<key>.+)/', banner_exempt(views.PayURecPayment.as_view()), name='club_payu_rec_payment'),
    url(r'platnosc/payu/(?P<key>.+)/', banner_exempt(views.PayUPayment.as_view()), name='club_payu_payment'),

    url(r'notify/(?P<pk>\d+)/', views.PayUNotifyView.as_view(), name='club_payu_notify'),

    url(r'czlonek/', views.MembershipView.as_view(), name='club_membership'),
]
