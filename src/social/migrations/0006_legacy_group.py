# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations


def legacy_group(apps, schema_editor):
    Cite = apps.get_model('social', 'Cite')
    BannerGroup = apps.get_model('social', 'BannerGroup')

    traditional = BannerGroup.objects.create(name='Tradycyjne cytaty')
    banners = BannerGroup.objects.create(name='Bannery')

    Cite.objects.exclude(book=None).update(group=traditional)
    Cite.objects.filter(book=None).update(group=banners)


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0005_auto_20190318_1309'),
    ]

    operations = [
        migrations.RunPython(
            legacy_group,
            migrations.RunPython.noop
        )
    ]
