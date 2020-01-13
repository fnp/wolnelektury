import json
from django.db import migrations


def populate_completed_at(apps, schema_editor):
    PayUOrder = apps.get_model('club', 'PayUOrder')
    for order in PayUOrder.objects.filter(status='COMPLETED'):
        for n in order.notification_set.order_by('received_at'):
            if json.loads(n.body)['order']['status'] == 'COMPLETED':
                order.completed_at = n.received_at
                order.save()
                break


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0022_payuorder_completed_at'),
    ]

    operations = [
        migrations.RunPython(
            populate_completed_at,
            migrations.RunPython.noop,
        )
    ]
