# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.urls import reverse


class PaymentMethod(object):
    is_onetime = False
    is_recurring = False

    def initiate(self, request, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


class PayU(PaymentMethod):
    is_onetime = True
    slug = 'payu'
    template_name = 'club/payment/payu.html'

    def __init__(self, pos_id):
        self.pos_id = pos_id

    def initiate(self, request, schedule):
        # Create Order at once.
        from .models import PayUOrder
        order = PayUOrder.objects.create(
            pos_id=self.pos_id,
            customer_ip=request.META['REMOTE_ADDR'],
            schedule=schedule,
        )
        return order.put()


class PayURe(PaymentMethod):
    slug='payu-re'
    template_name = 'club/payment/payu-re.html'
    is_recurring = True

    def __init__(self, pos_id):
        self.pos_id = pos_id

    def initiate(self, request, schedule):
        return reverse('club_payu_rec_payment', args=[schedule.key])

    def pay(self, request, schedule):
        # Create order, put it and see what happens next.
        from .models import PayUOrder
        if request is not None:
            ip = request.META['REMOTE_ADDR']
        else:
            ip = '127.0.0.1'
        order = PayUOrder.objects.create(
            pos_id=self.pos_id,
            customer_ip=ip,
            schedule=schedule,
        )
        return order.put()
        

class PayPal(PaymentMethod):
    slug='paypal'
    template_name = 'club/payment/paypal.html'
    is_recurring = True
    is_onetime = True

    def initiate(self, request, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


pos = getattr(settings, 'CLUB_PAYU_RECURRING_POS', None)
if pos:
    recurring_payment_method = PayURe(pos)
else:
    recurring_payment_method = None

pos = getattr(settings, 'CLUB_PAYU_POS', None)
if pos:
    single_payment_method = PayU(pos)
else:
    single_payment_method = None
