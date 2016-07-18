# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _


def unsubscribe(request):
    return render(request, 'newsletter/unsubscribe.html', {
        'page_title': _(u'Unsubscribe'),
    })