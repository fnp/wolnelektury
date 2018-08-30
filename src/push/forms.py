# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import forms
from django.contrib.sites.models import Site

from push.models import Notification
from push.utils import send_fcm_push


class NotificationForm(forms.ModelForm):

    class Meta:
        model = Notification
        exclude = ('timestamp', 'message_id')

    def save(self, commit=True):
        notification = super(NotificationForm, self).save(commit=commit)
        wl_base = u'https://' + Site.objects.get_current().domain
        notification.message_id = send_fcm_push(notification.title, notification.body, wl_base + notification.image.url)
        if commit:
            notification.save()
