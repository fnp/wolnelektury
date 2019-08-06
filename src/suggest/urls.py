# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf.urls import url
from suggest import views

urlpatterns = [
    url(r'^$', views.SuggestionFormView(), name='suggest'),
    url(r'^plan/$', views.PublishingSuggestionFormView(), name='suggest_publishing'),
]
