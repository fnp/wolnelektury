# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayUCardToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disposable_token', models.CharField(max_length=255, unique=True)),
                ('reusable_token', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayUNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('received_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayUOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos_id', models.CharField(max_length=255)),
                ('customer_ip', models.GenericIPAddressField()),
                ('amount', models.PositiveIntegerField()),
                ('order_id', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('WAITING_FOR_CONFIRMATION', 'Waiting for confirmation'), ('COMPLETED', 'Completed'), ('CANCELED', 'Canceled'), ('REJECTED', 'Rejected')], max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='payment',
            name='schedule',
        ),
        migrations.AddField(
            model_name='membership',
            name='honorary',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='plan',
            name='active',
            field=models.BooleanField(default=True, verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='method',
            field=models.CharField(choices=[('payu-re', 'PayU Recurring'), ('paypal-re', 'PayPal Recurring')], max_length=255, verbose_name='method'),
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.AddField(
            model_name='payuorder',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Schedule'),
        ),
        migrations.AddField(
            model_name='payunotification',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.PayUOrder'),
        ),
        migrations.AddField(
            model_name='payucardtoken',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='club.Schedule'),
        ),
    ]
