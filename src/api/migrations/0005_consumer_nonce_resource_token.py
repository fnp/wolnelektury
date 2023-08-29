# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0004_bookuserdata_last_changed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('key', models.CharField(max_length=18)),
                ('secret', models.CharField(max_length=32)),
                ('status', models.CharField(choices=[('pending', 'Pending approval'), ('accepted', 'Accepted'), ('canceled', 'Canceled')], default='pending', max_length=16)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='consumers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Nonce',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_key', models.CharField(max_length=18)),
                ('consumer_key', models.CharField(max_length=18)),
                ('key', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=18)),
                ('secret', models.CharField(max_length=32)),
                ('token_type', models.IntegerField(choices=[(1, 'Request'), (2, 'Access')])),
                ('timestamp', models.IntegerField()),
                ('is_approved', models.BooleanField(default=False)),
                ('consumer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Consumer')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
