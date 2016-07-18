# -*- coding: utf-8 -*-
from django.db.models import Model, EmailField, DateTimeField, BooleanField
from django.utils.translation import ugettext_lazy as _


class Subscription(Model):
    email = EmailField(verbose_name=_('email address'))
    active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    last_modified = DateTimeField(auto_now=True)
