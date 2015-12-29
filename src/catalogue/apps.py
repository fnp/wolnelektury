# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import AppConfig

class CatalogueConfig(AppConfig):
    name = 'catalogue'

    def ready(self):
        from . import signals
