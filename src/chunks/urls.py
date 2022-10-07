# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.urls import path
from . import views

urlpatterns = [
        path('attachment/<key>.<slug:ext>', views.attachment, name='chunks_attachment'),
]