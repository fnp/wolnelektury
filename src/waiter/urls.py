# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from waiter import views

urlpatterns = [
    path('<path:path>', views.wait, name='waiter'),
]
