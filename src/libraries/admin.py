# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.contrib import admin

from libraries.models import Library, Catalog


admin.site.register(Catalog)
admin.site.register(Library)
