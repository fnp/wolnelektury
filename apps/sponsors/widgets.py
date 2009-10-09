from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from sponsors import models


class OrderedSelectMultiple(forms.TextInput):
    """
    A SelectMultiple with a JavaScript interface.
    """
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.1/jquery-ui.min.js',
            settings.MEDIA_URL + 'js/ordered_select_multiple.js',
        )

    def render(self, name, value, attrs=None, choices=()):
        output = [super(OrderedSelectMultiple, self).render(name, value, attrs)]
        choices = [(unicode(obj), obj.pk) for obj in models.Sponsor.objects.all()]
        choices_js = ', '.join('{name: "%s", id: %d}' % choice for choice in choices)
        output.append(u'<script type="text/javascript">addEvent(window, "load", function(e) {')
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append(u'$("#id_%s").orderedSelectMultiple({choices: [%s]}); });</script>\n' % 
            (name, choices_js))
        return mark_safe(u''.join(output))

