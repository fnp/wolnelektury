# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClubConfig(AppConfig):
    name = 'club'
    verbose_name = _('Club')
