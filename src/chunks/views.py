# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import HttpResponse
from ssify import ssi_included
from .models import Chunk

@ssi_included
def chunk(request, key):
    chunk, created = Chunk.objects.get_or_create(key=key)
    return HttpResponse(chunk.content)
