# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from .pos import POS


POSS = {
    k: POS(k, **v)
    for (k, v) in settings.PAYU_POS.items()
}
