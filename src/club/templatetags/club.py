# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from ..helpers import get_active_schedule


register = template.Library()


@register.filter
def active_schedule(user):
    return get_active_schedule(user)
