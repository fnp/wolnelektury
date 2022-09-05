# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from django.views.generic import RedirectView
from annoy.utils import banner_exempt
from . import views


urlpatterns = [
    path('', banner_exempt(views.JoinView.as_view()), name='club_join'),
    path('dolacz/', RedirectView.as_view(
        url='/pomagam/', permanent=False)),
    path('info/', banner_exempt(views.ClubView.as_view()), name='club'),

    path('plan/<key>/', banner_exempt(views.ScheduleView.as_view()), name='club_schedule'),
    path('plan/<key>/dziekujemy/', banner_exempt(views.ScheduleThanksView.as_view()), name='club_thanks'),
    path('plan/<key>/zestawienie/<int:year>/', banner_exempt(views.YearSummaryView.as_view()), name='club_year_summary'),
    path('plan/<key>/rodzaj/', banner_exempt(views.DonationStep1.as_view()), name='donation_step1'),
    path('plan/<key>/dane/', banner_exempt(views.DonationStep2.as_view()), name='donation_step2'),

    path('przylacz/<key>/', views.claim, name='club_claim'),
    path('anuluj/<key>/', views.cancel, name='club_cancel'),
    path('testowa-platnosc/<key>/', views.DummyPaymentView.as_view(), name='club_dummy_payment'),

    path('platnosc/payu/cykl/<key>/', banner_exempt(views.PayURecPayment.as_view()), name='club_payu_rec_payment'),
    path('platnosc/payu/<key>/', banner_exempt(views.PayUPayment.as_view()), name='club_payu_payment'),

    path('notify/<int:pk>/', views.PayUNotifyView.as_view(), name='club_payu_notify'),

    path('weryfikacja/', views.member_verify, name='club_member_verify'),
]
