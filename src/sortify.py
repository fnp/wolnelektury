# -*- coding: utf-8 -*-
import re
from fnpdjango.utils.text.slughifi import char_map


# Specifies diacritics order.
# Default order is zero, max is 9
char_order = {
    u'ż': 1, u'Ż': 1,
}


def replace_char(m):
    char = m.group()
    if char in char_map:
        order = char_order.get(char, 0)
        return "%s~%d" % (char_map[char], order)
    else:
        return char


def sortify(value):
    """
        Turns Unicode into ASCII-sortable str

        Examples :

        >>> sortify('a a') < sortify('aa') < sortify('ą') < sortify('b')
        True

        >>> sortify('ź') < sortify('ż')
        True

    """

    if not isinstance(value, unicode):
        value = unicode(value, 'utf-8')

    # try to replace chars
    value = re.sub('[^a-zA-Z0-9\\s\\-]', replace_char, value)
    value = value.lower()
    value = re.sub(r'[^a-z0-9~]+', ' ', value)
    
    return value.encode('ascii', 'ignore')
