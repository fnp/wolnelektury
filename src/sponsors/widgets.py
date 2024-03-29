# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe

from sponsors import models


class SponsorPageWidget(forms.Textarea):
    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
            '//code.jquery.com/ui/1.12.1/jquery-ui.min.js',
            settings.STATIC_URL + 'sponsors/js/jquery.json.min.js',
            settings.STATIC_URL + 'sponsors/js/footer_admin.js',
        )
        css = {
            'all': (settings.STATIC_URL + 'sponsors/css/footer_admin.css',),
        }

    def render(self, name, value, attrs=None, renderer=None):
        output = [super(SponsorPageWidget, self).render(name, value, attrs, renderer)]
        sponsors = [(str(obj), obj.pk, obj.logo.url) for obj in models.Sponsor.objects.all().iterator()]
        sponsors_js = ', '.join('{name: "%s", id: %d, image: "%s"}' % sponsor for sponsor in sponsors)
        output.append('<script type="text/javascript">$(function(e) {')
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('$("#id_%s").sponsorsFooter({sponsors: [%s]}); });</script>\n' % (name, sponsors_js))
        return mark_safe(''.join(output))
