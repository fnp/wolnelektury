import re
from fnpdjango.utils.text import char_map


# Specifies diacritics order.
# Default order is zero, max is 9
char_order = {
    'ż': 1, 'Ż': 1,
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

    if not isinstance(value, str):
        value = str(value, 'utf-8')

    # try to replace chars
    value = re.sub('[^a-zA-Z0-9\\s\\-]', replace_char, value)
    value = value.lower()
    value = re.sub(r'[^a-z0-9~]+', ' ', value)
    
    return value.encode('ascii', 'ignore').decode('ascii')
