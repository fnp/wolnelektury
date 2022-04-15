# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from django.core.management.base import BaseCommand
from club.models import PayUOrder


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--rejected', '-r', type=bool, default=False)
        parser.add_argument('order_id', type=int)
    
    def handle(self, **options):
        order = PayUOrder.objects.get(id=options['order_id'])
        status = 'REJECTED' if options['rejected'] else 'COMPLETED'
        notification = order.notification_set.create(
            body=json.dumps({
                'order': {
                    'status': status,
                    'fake': True,
                }
            })
        )
        notification.apply()
