# -*- coding: utf-8 -*-
import hashlib

from django.db.models import Model, EmailField, DateTimeField, BooleanField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Subscription(Model):
    email = EmailField(verbose_name=_('email address'), unique=True)
    active = BooleanField(default=True, verbose_name=_(u'active'))
    created_at = DateTimeField(auto_now_add=True)
    last_modified = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def __str__(self):
        return self.email

    def hashcode(self):
        return hashlib.sha224(self.email + settings.SECRET_KEY).hexdigest()[:30]
