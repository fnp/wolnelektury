# Generated by Django 2.2.28 on 2022-10-03 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0007_auto_20221003_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='funding',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='funding',
            name='customer_ip',
            field=models.GenericIPAddressField(null=True, verbose_name='customer IP'),
        ),
        migrations.AddField(
            model_name='funding',
            name='order_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='order ID'),
        ),
        migrations.AddField(
            model_name='funding',
            name='pos_id',
            field=models.CharField(default='', max_length=255, verbose_name='POS id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='funding',
            name='status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('WAITING_FOR_CONFIRMATION', 'Waiting for confirmation'), ('COMPLETED', 'Completed'), ('CANCELED', 'Canceled'), ('REJECTED', 'Rejected'), ('ERR-INVALID_TOKEN', 'Invalid token')], max_length=128),
        ),
        migrations.AlterField(
            model_name='funding',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='PayUNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='body')),
                ('received_at', models.DateTimeField(auto_now_add=True, verbose_name='received_at')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_set', to='funding.Funding')),
            ],
            options={
                'verbose_name': 'PayU notification',
                'verbose_name_plural': 'PayU notifications',
                'abstract': False,
            },
        ),
    ]
