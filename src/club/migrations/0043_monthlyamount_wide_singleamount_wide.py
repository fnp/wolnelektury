# Generated by Django 4.0.8 on 2023-05-08 12:46

from django.db import migrations, models


def last_amount_wide(apps, schema_editor):
    SingleAmount = apps.get_model('club', 'SingleAmount')
    a = SingleAmount.objects.last()
    if a is not None:
        a.wide = True
        a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0042_auto_20220826_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyamount',
            name='wide',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='singleamount',
            name='wide',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            last_amount_wide,
            migrations.RunPython.noop
        )
    ]
