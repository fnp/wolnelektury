# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.apps import AppConfig


class WLCoreConfig(AppConfig):
    name = 'wolnelektury'

    def ready(self):
        from . import signals
