# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe

from sponsors import models


class SponsorPageWidget(forms.Textarea):
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.1/jquery-ui.min.js',
            settings.STATIC_URL + 'sponsors/js/jquery.json.min.js',
            settings.STATIC_URL + 'sponsors/js/footer_admin.js',
        )
        css = {
            'all': (settings.STATIC_URL + 'sponsors/css/footer_admin.css',),
        }

    def render(self, name, value, attrs=None):
        output = [super(SponsorPageWidget, self).render(name, value, attrs)]
        sponsors = [(unicode(obj), obj.pk, obj.logo.url) for obj in models.Sponsor.objects.all().iterator()]
        sponsors_js = ', '.join('{name: "%s", id: %d, image: "%s"}' % sponsor for sponsor in sponsors)
        output.append(u'<script type="text/javascript">addEvent(window, "load", function(e) {')
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append(u'$("#id_%s").sponsorsFooter({sponsors: [%s]}); });</script>\n' %
            (name, sponsors_js))
        return mark_safe(u''.join(output))
