# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.template import Library
from contact.models import Contact

register = Library()


@register.filter
def pretty_print(value):
    return Contact.pretty_print(value)
