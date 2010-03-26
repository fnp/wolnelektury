#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import httplib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import sys
import getpass

register_openers()

datagen, headers = multipart_encode({'book_xml_file': open(sys.argv[1], "rb")})
data = ''.join(list(datagen))
for key, value in headers.items():
    headers[key] = str(value)

password = getpass.getpass()

h = httplib2.Http()
h.add_credentials('zuber', password)
h.follow_all_redirects = True

resp, content = h.request(
    'http://localhost:8000/api/books.json',
    'POST',
    body=data,
    headers=headers
)
print resp, content