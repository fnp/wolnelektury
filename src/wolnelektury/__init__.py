# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from .celery import app as celery_app

default_app_config = 'wolnelektury.apps.WLCoreConfig'
