# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
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
        wl_base = 'https://' + Site.objects.get_current().domain
        if notification.image:
            image_url = wl_base + notification.image.url
        else:
            image_url = None
        notification.message_id = send_fcm_push(notification.title, notification.body, image_url)
        if commit:
            notification.save()
