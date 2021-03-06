# Generated by Django 2.2.6 on 2019-11-27 08:49

from django.db import migrations


def migrate_plans(apps, schema_editor):
    Schedule = apps.get_model('club', 'Schedule')
    schedules = Schedule.objects.filter(method='payu-re')
    schedules.filter(plan__interval=30).update(monthly=True)
    schedules.filter(plan__interval=365).update(yearly=True)


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0015_auto_20191127_0947'),
    ]

    operations = [
        migrations.RunPython(
            migrate_plans,
            migrations.RunPython.noop,
            elidable=True,
        )
    ]
