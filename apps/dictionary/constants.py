# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _


FN_TYPES = {
    'pa': _("author's footnotes"),
    'pe': _("Wolne Lektury editorial footnotes"),
    'pr': _("source editorial footnotes"),
    'pt': _("translator's footnotes"),
}
