# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from . import views


urlpatterns = [
    path('<slug:key>/books/',
        views.PartnerBooksView.as_view()),
]
