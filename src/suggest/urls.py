# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from suggest import views

urlpatterns = [
    path('', views.SuggestionFormView(), name='suggest'),
    path('plan/', views.PublishingSuggestionFormView(), name='suggest_publishing'),
]
