# -*- coding: utf-8
import re
import string
from fnpdjango.utils.text.slughifi import char_map

# PayU chokes on non-Polish diacritics.
# Punctuation is handled correctly and escaped as needed,
# with the notable exception of backslash.
sane_in_payu_title = re.escape(
    string.uppercase +
    string.lowercase + 
    u'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ' + 
    string.digits +
    ' ' +
    "".join(set(string.punctuation) - set('\\'))
)

def replace_char(m):
    char = m.group()
    return char_map.get(char, '')

def sanitize_payment_title(value):
    return re.sub('[^%s]{1}' % sane_in_payu_title, replace_char, unicode(value))
