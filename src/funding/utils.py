# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import re
import string
from fnpdjango.utils.text import char_map

# PayU chokes on non-Polish diacritics.
# Punctuation is handled correctly and escaped as needed,
# with the notable exception of backslash.
sane_in_payu_title = re.escape(
    string.ascii_uppercase +
    string.ascii_lowercase +
    u'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ' +
    string.digits +
    ' ' +
    "".join(set(string.punctuation) - set('\\'))
)


def replace_char(m):
    char = m.group()
    return char_map.get(char, '')


def sanitize_payment_title(value):
    return re.sub('[^%s]' % sane_in_payu_title, replace_char, str(value))
