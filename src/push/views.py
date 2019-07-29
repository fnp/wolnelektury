# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.decorators import permission_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from push.forms import NotificationForm


@permission_required('push.change_notification')
def notification_form(request):
    if request.method == 'POST':
        form = NotificationForm(data=request.POST, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('notification_sent'))
    else:
        form = NotificationForm()
    return render(request, 'push/notification_form.html', {'form': form})


def notification_sent(request):
    return render(request, 'push/notification_sent.html')
