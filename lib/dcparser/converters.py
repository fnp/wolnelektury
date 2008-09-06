# -*- coding: utf-8 -*-
from datetime import date
import time
import re


class Person(object):
    """Single person with last name and a list of first names."""
    def __init__(self, last_name, *first_names):
        self.last_name = last_name
        self.first_names = first_names
    
    
    def __eq__(self, right):
        return self.last_name == right.last_name and self.first_names == right.first_names
    
    
    def __unicode__(self):
        if len(self.first_names) > 0:
            return '%s, %s' % (self.last_name, ' '.join(self.first_names))
        else:
            return self.last_name
    
    
    def __repr__(self):
        return 'Person(last_name=%r, first_names=*%r)' % (self.last_name, self.first_names)


def str_to_unicode(value, previous):
    return unicode(value)


def str_to_person(value, previous):
    comma_count = value.count(',')
    
    if comma_count == 0:
        last_name, first_names = value, []
    elif comma_count == 1:
        last_name, first_names = value.split(',')
        first_names = [name for name in first_names.split(' ') if len(name)]
    else:
        raise ValueError("value contains more than one comma: %r" % value)
    
    return Person(last_name.strip(), *first_names)


def str_to_date(value, previous):
    try:
        t = time.strptime(value, '%Y-%m-%d')
    except ValueError:
        t = time.strptime(value, '%Y')
    return date(t[0], t[1], t[2])


