# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from annoy.utils import banner_exempt
from . import views


urlpatterns = [
    path('<slug>/', banner_exempt(views.infopage), name='infopage'),
]
