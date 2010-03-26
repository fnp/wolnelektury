#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from lxml import etree
from slughifi import slughifi
from django.core.management import setup_environ
from wolnelektury import settings

setup_environ(settings)

from catalogue.models import Tag


doc = etree.parse('rodziny.xml')

for element in doc.findall('//span'):
    themes = [s.strip() for s in element.text.split(',')]
    
    element.text = u''
    
    for theme in themes:
        try:
            Tag.objects.get(slug=slughifi(theme))
        
            link = etree.SubElement(element, 'a', href=u'/katalog/%s' % slughifi(theme))
            link.text = theme
            link.tail = ', '
            last_link = link
        except:
            print "Pomijam %s" % slughifi(theme)

    last_link.tail = ''


doc.write('ok.xml', xml_declaration=False, pretty_print=True, encoding='utf-8')
