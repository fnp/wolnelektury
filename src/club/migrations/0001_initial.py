# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'membership',
                'verbose_name_plural': 'memberships',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('payed_at', models.DateTimeField(blank=True, null=True, verbose_name='payed at')),
            ],
            options={
                'verbose_name': 'payment',
                'verbose_name_plural': 'payments',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval', models.SmallIntegerField(choices=[(30, 'a month'), (365, 'a year'), (999, 'in perpetuity')], verbose_name='inteval')),
                ('min_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='min_amount')),
                ('allow_recurring', models.BooleanField(verbose_name='allow recurring')),
                ('allow_one_time', models.BooleanField(verbose_name='allow one time')),
            ],
            options={
                'ordering': ('interval',),
            },
        ),
        migrations.CreateModel(
            name='ReminderEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_before', models.SmallIntegerField(verbose_name='days before')),
                ('subject', models.CharField(max_length=1024, verbose_name='subject')),
                ('subject_de', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_en', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_es', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_fr', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_it', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_lt', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_pl', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_ru', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('subject_uk', models.CharField(max_length=1024, null=True, verbose_name='subject')),
                ('body', models.TextField(verbose_name='body')),
                ('body_de', models.TextField(null=True, verbose_name='body')),
                ('body_en', models.TextField(null=True, verbose_name='body')),
                ('body_es', models.TextField(null=True, verbose_name='body')),
                ('body_fr', models.TextField(null=True, verbose_name='body')),
                ('body_it', models.TextField(null=True, verbose_name='body')),
                ('body_lt', models.TextField(null=True, verbose_name='body')),
                ('body_pl', models.TextField(null=True, verbose_name='body')),
                ('body_ru', models.TextField(null=True, verbose_name='body')),
                ('body_uk', models.TextField(null=True, verbose_name='body')),
            ],
            options={
                'ordering': ['days_before'],
                'verbose_name': 'reminder email',
                'verbose_name_plural': 'reminder emails',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255, unique=True, verbose_name='key')),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='amount')),
                ('method', models.CharField(choices=[('payu', 'PayU'), ('payu-re', 'PayU Recurring'), ('paypal-re', 'PayPal Recurring')], max_length=255, verbose_name='method')),
                ('is_active', models.BooleanField(default=False, verbose_name='active')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='cancelled')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='started at')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expires_at')),
                ('membership', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='club.Membership', verbose_name='membership')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='club.Plan', verbose_name='plan')),
            ],
            options={
                'verbose_name': 'schedule',
                'verbose_name_plural': 'schedules',
            },
        ),
        migrations.AddField(
            model_name='payment',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='club.Schedule', verbose_name='schedule'),
        ),
    ]
