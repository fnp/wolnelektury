# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import timedelta
from django.db.models import Sum
from django import template
from django.utils.timezone import now
from ..helpers import get_active_schedule
from ..models import Schedule


register = template.Library()


@register.filter
def active_schedule(user):
    return get_active_schedule(user)


@register.simple_tag
def club_active_monthly_count():
    return Schedule.objects.filter(
        expires_at__gt=now(),
        monthly=True,
        is_cancelled=False
    ).count()

@register.simple_tag
def club_active_monthly_sum():
    return Schedule.objects.filter(
        expires_at__gt=now(),
        monthly=True,
        is_cancelled=False
    ).aggregate(s=Sum('amount'))['s'] or 0

@register.simple_tag
def club_active_yearly_count():
    return Schedule.objects.filter(
        expires_at__gt=now(),
        yearly=True,
        is_cancelled=False
    ).count()

@register.simple_tag
def club_active_yearly_sum():
    return Schedule.objects.filter(
        expires_at__gt=now(),
        yearly=True,
        is_cancelled=False
    ).aggregate(s=Sum('amount'))['s'] or 0

@register.simple_tag
def club_active_30day_count():
    return Schedule.objects.filter(
        yearly=False, monthly=False,
        payed_at__gte=now() - timedelta(days=30)
    ).count()

@register.simple_tag
def club_active_30day_sum():
    return Schedule.objects.filter(
        yearly=False, monthly=False,
        payed_at__gte=now() - timedelta(days=30)
    ).aggregate(s=Sum('amount'))['s'] or 0
