# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from glob import glob
from os import path
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Check snippets.'

    def handle(self, *args, **opts):
        sfn = glob(settings.SEARCH_INDEX+'snippets/*')
        for fn in sfn:
            print(fn)
            bkid = path.basename(fn)
            with open(fn) as f:
                cont = f.read()
                try:
                    cont.decode('utf-8')
                except UnicodeDecodeError:
                    print("error in snippets %s" % bkid)
