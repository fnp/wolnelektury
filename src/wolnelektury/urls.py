# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
import django.views.static
from annoy.utils import banner_exempt
import catalogue.views
import picture.views
from . import views


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('planowane/', views.publish_plan, name='publish_plan'),
    path('widget.html', views.widget, name='widget'),

    path('zegar/', views.clock, name='clock'),

    # Authentication
    path('uzytkownik/', views.user_settings, name='user_settings'),
    path('uzytkownik/login/', banner_exempt(views.LoginFormView()), name='login'),
    path('uzytkownik/signup/', banner_exempt(views.RegisterFormView()), name='register'),
    path('uzytkownik/logout/', views.logout_then_redirect, name='logout'),
    path('uzytkownik/zaloguj-utworz/', banner_exempt(views.LoginRegisterFormView()), name='login_register'),
    path('uzytkownik/social/signup/', banner_exempt(views.SocialSignupView.as_view()), name='socialaccount_signup'),
]

urlpatterns += [
    path('katalog/', include('catalogue.urls')),
    path('opds/', include('opds.urls')),
    path('sugestia/', include('suggest.urls')),
    path('lesmianator/', include('lesmianator.urls')),
    path('przypisy/', include('dictionary.urls')),
    path('raporty/', include('reporting.urls')),
    path('info/', include('infopages.urls')),
    path('ludzie/', include('social.urls')),
    path('uzytkownik/', include('allauth.urls')),
    path('czekaj/', include('waiter.urls')),
    path('wesprzyj/', include('funding.urls')),
    path('ankieta/', include('polls.urls')),
    path('biblioteki/', include('libraries.urls')),
    path('newsletter/', include('newsletter.urls')),
    path('formularz/', include('forms_builder.forms.urls')),
    path('isbn/', include('isbn.urls')),
    path('messaging/', include('messaging.urls')),
    path('re/', include('redirects.urls')),

    path('paypal/app-form/', RedirectView.as_view(
        url='/towarzystwo/?pk_campaign=aplikacja', permanent=False)),
    path('towarzystwo/dolacz/', RedirectView.as_view(
        url='/towarzystwo/', permanent=False)),

    path('paypal/', include('paypal.urls')),
    path('powiadomienie/', include('push.urls')),
    path('towarzystwo/', include('club.urls')),

    # Admin panel
    path('admin/catalogue/book/import', catalogue.views.import_book, name='import_book'),
    path('admin/catalogue/picture/import', picture.views.import_picture, name='import_picture'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    # API
    path('api/', include('api.urls')),
    # OAIPMH
    path('oaipmh/', include('oai.urls')),

    path('szukaj/', include('search.urls')),

    path('i18n/', include('django.conf.urls.i18n')),
    path('forum/', include('machina.urls')),
]

urlpatterns += [
    # old static pages - redirected
    path('1procent/', RedirectView.as_view(
        url='http://nowoczesnapolska.org.pl/wesprzyj_nas/', permanent=True)),
    path('epub/', RedirectView.as_view(
        url='/katalog/lektury/', permanent=False)),
    path('mozesz-nam-pomoc/', RedirectView.as_view(
        url='/info/wlacz-sie-w-prace/', permanent=True)),
    path('o-projekcie/', RedirectView.as_view(
        url='/info/o-projekcie/', permanent=True)),
    path('widget/', RedirectView.as_view(
        url='/info/widget/', permanent=True)),
    path('wolontariat/', RedirectView.as_view(
        url='/info/wlacz-sie-w-prace/', permanent=False)),
]

urlpatterns += [
    # path('error-test/', views.exception_test),
    # path('post-test/', views.post_test),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += [
        # Static files
        path('%s<path:path>' % settings.MEDIA_URL[1:], django.views.static.serve,
           {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
