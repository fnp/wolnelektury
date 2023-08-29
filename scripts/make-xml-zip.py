#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import os
import django
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wolnelektury.settings")
django.setup()

from catalogue.models import Book


if len(sys.argv) < 2:
    print "Provide a zip name as first argument"
    sys.exit(-1)

zip = zipfile.ZipFile(sys.argv[1], 'w')
for book in Book.objects.all():
    zip.write(book.xml_file.path, "%s.xml" % book.slug)
zip.close()

