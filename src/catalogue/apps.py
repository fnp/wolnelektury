# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    name = 'catalogue'

    def ready(self):
        from . import signals
