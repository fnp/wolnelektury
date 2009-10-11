#!/usr/bin/env python
import sys

from django.core.management import setup_environ
from wolnelektury import settings
try:
    set
except AttributeError:
    from set import Set as set

setup_environ(settings)

from catalogue import models

fragment_identifiers = set()

print
print 'Before: %d fragments' % models.Fragment.objects.count()
print

for fragment in models.Fragment.objects.all():
    if (fragment.book_id, fragment.anchor) in fragment_identifiers:
        fragment.delete()
        sys.stderr.write('X')
    else:
        fragment_identifiers.add((fragment.book_id, fragment.anchor))
        sys.stderr.write('.')

print
print 'After: %d fragments' % models.Fragment.objects.count()
print