#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import sys
sys.path.insert(0, '../apps')
sys.path.insert(0, '../lib')
sys.path.insert(0, '../lib/librarian')
sys.path.insert(0, '../wolnelektury')
sys.path.insert(0, '..')

from django.core.management import setup_environ
from wolnelektury import settings
import sys
import zipfile

setup_environ(settings)

from catalogue.models import Book


if len(sys.argv) < 2:
    print "Provide a zip name as first argument"
    sys.exit(-1)

zip = zipfile.ZipFile(sys.argv[1], 'w')
for book in Book.objects.all():
    zip.write(book.xml_file.path, "%s.xml" % book.slug)
zip.close()

