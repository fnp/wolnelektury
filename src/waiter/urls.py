# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.urls import path
from waiter import views

urlpatterns = [
    path('<path:path>', views.wait, name='waiter'),
]
