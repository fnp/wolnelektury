# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib import admin

from libraries.models import Library, Catalog


admin.site.register(Catalog)
admin.site.register(Library)
