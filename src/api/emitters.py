# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""
Wrappers for piston Emitter classes.
"""
from piston.emitters import Emitter


# hack
class EpubEmitter(Emitter):
    def render(self, request):
        return self.data

Emitter.register('epub', EpubEmitter, 'application/epub+zip')
