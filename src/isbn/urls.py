# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from . import views

urlpatterns = (
    url(r'^dodaj/$', views.add_isbn_wl, name='add_isbn_wl'),
    url(r'^potwierdzenie/$', views.confirm_isbn_wl, name='confirm_isbn_wl'),
    url(r'^save-wl-onix/$', views.save_wl_onix, name='save_wl_onix'),
    url(r'^tagi-isbn/(?P<slug>[a-z0-9-]*)/$', views.wl_dc_tags, name='wl_dc_tags'),

    url(r'^dodaj-fnp/$', views.add_isbn_fnp, name='add_isbn_fnp'),
    url(r'^przypisane/(?P<slug>[a-z0-9-]*)/$', views.assigned_isbn, name='assigned_isbn'),
)
