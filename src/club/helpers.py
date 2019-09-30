# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.utils.timezone import now
from .models import Schedule


def get_active_schedule(user):
    if not user.is_authenticated:
        return None
    return Schedule.objects.filter(
            membership__user=user
        ).exclude(payed_at=None).exclude(expires_at__lt=now()).first()

