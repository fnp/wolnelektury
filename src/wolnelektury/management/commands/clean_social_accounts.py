# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from allauth.socialaccount.models import SocialAccount
from django.core.management.base import BaseCommand


KEPT_FIELDS = {
    'facebook': ['link', 'name', 'id', 'locale', 'timezone', 'updated_time', 'verified'],
    'google': ['name', 'picture', 'locale', 'id', 'verified_email', 'link'],
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        for provider, kept_fields in KEPT_FIELDS.items():
            for sa in SocialAccount.objects.filter(provider=provider):
                trimmed_data = {k: v for k, v in sa.extra_data.items() if k in kept_fields}
                sa.extra_data = trimmed_data
                sa.save()
