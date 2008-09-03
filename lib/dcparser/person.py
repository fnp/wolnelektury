# -*- coding: utf-8 -*-


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

