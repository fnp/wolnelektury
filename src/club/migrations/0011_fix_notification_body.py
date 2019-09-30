# Generated by Django 2.2.5 on 2019-09-30 13:02

from django.db import migrations


def fix_notification_body(apps, schema_editor):
    PayUNotification = apps.get_model('club', 'PayUNotification')
    for n in PayUNotification.objects.filter(body__startswith='b'):
        n.body = n.body[2:-1]
        n.save()


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0010_auto_20190529_0946'),
    ]

    operations = [
        migrations.RunPython(
            fix_notification_body,
            migrations.RunPython.noop,
            elidable=True),
    ]
