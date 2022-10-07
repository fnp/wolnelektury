# Generated by Django 2.2.27 on 2022-04-20 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0038_payuorder_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payuorder',
            name='status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('WAITING_FOR_CONFIRMATION', 'Waiting for confirmation'), ('COMPLETED', 'Completed'), ('CANCELED', 'Canceled'), ('REJECTED', 'Rejected'), ('ERR-INVALID_TOKEN', 'Invalid token')], max_length=128),
        ),
    ]