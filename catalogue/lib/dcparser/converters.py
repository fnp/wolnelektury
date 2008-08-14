# -*- coding: utf-8 -*-
from datetime import date
import time
import re

from person import Person


def str_to_unicode(value):
    return unicode(value)


def str_to_person(value):
    comma_count = value.count(',')
    
    if comma_count == 0:
        last_name, first_names = value, []
    elif comma_count == 1:
        last_name, first_names = value.split(',')
        first_names = [name for name in first_names.split(' ') if len(name)]
    else:
        raise ValueError("value contains more than one comma: %r" % value)
    
    return Person(last_name.strip(), *first_names)


def str_to_date(value):
    try:
        t = time.strptime(value, '%Y-%m-%d')
    except ValueError:
        t = time.strptime(value, '%Y')
    return date(t[0], t[1], t[2])


