#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management import setup_environ
from wolnelektury import settings
import sys

setup_environ(settings)

from catalogue.models import Tag


MAIN_PAGE_THEMES = [
    u'Obywatel',
    u'Car',
    u'Błoto',
    u'Krew',
    u'Danse macabre',
    u'Obcy',
    u'Matka',
    u'Gotycyzm',
]


for tag in Tag.objects.all():
    if tag.category in ('epoch', 'genre', 'author', 'kind'):
        tag.main_page = True
    elif tag.category == 'theme' and tag.name in MAIN_PAGE_THEMES:
        tag.main_page = True
    else:
        tag.main_page = False
    
    tag.save()
    sys.stderr.write('.')


