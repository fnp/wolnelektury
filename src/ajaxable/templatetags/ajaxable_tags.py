# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django import template
from django.utils.safestring import mark_safe

from ajaxable.utils import placeholdized
register = template.Library()


@register.filter
def placeholdize(form):
    return placeholdized(form)


@register.filter
def placeholdized_ul(form):
    return placeholdized(form).as_ul()


@register.filter
def pretty_field(field, template=None):
    if template is None:
        template = '''
            <li>
              <span class="error">%(errors)s</span>
              <label class="nohide"><span class="label">%(label)s: </span>%(input)s</label>
              <span class="helptext">%(helptext)s</span>
            </li>'''
    return mark_safe(template % {
        'errors': field.errors,
        'input': field,
        'label': field.label,
        'helptext': field.help_text,
    })


@register.filter
def pretty_checkbox(field):
    return pretty_field(field, template='''
        <li class="checkbox">
          <span class="error">%(errors)s</span>
          <label class="nohide">%(input)s<span class="label"> %(label)s</span></label>
          <span class="helptext">%(helptext)s</span>
        </li>''')
