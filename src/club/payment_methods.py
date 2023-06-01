# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from hashlib import sha256
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import get_language
from paypal.rest import agreement_approval_url
from django.template.loader import render_to_string
from .payu import POSS


class PaymentMethod(object):
    is_onetime = False
    is_recurring = False
    expiration_reliable = False
    cancellable = False
    updateable = False

    def initiate(self, request, schedule):
        return reverse('club_dummy_payment', args=[schedule.key])


class PayU(PaymentMethod):
    is_onetime = True
    expiration_reliable = True
    slug = 'payu'
    name = 'PayU'
    template_name = 'club/payment/payu.html'

    def __init__(self, pos_id):
        self.pos_id = pos_id

    def invite_widget(self, schedule, request):
        return render_to_string(
            'club/payment/payu_invite.html',
            {
                'schedule': schedule,
            },
            request=request
        )

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
    slug = 'payu-re'
    name = 'PayU recurring'
    template_name = 'club/payment/payu-re.html'
    is_recurring = True
    expiration_reliable = True
    cancellable = True
    updateable = True

    def __init__(self, pos_id):
        self.pos_id = pos_id

    def initiate(self, request, schedule):
        return reverse('club_payu_rec_payment', args=[schedule.key])

    def invite_widget(self, schedule, request):
        from . import forms
        pos = POSS[self.pos_id]
        widget_args = {
            'merchant-pos-id': pos.pos_id,
            'shop-name': "SHOW NAME",
            'total-amount': str(int(schedule.amount * 100)),
            'currency-code': pos.currency_code,
            'customer-language': get_language(), # filter to pos.languages
            'customer-email': schedule.email,
            'store-card': 'true',
            'recurring-payment': 'true',
        }
        widget_sig = sha256(
            (
                "".join(v for (k, v) in sorted(widget_args.items())) +
                pos.secondary_key
            ).encode('utf-8')
        ).hexdigest()
        
        return render_to_string(
            'payu/rec_widget.html',
            {
                'schedule': schedule,
                'form': forms.PayUCardTokenForm(),
                'pos': POSS[self.pos_id],
                'widget_args': widget_args,
                'widget_sig': widget_sig,
            },
            request=request
        )

    def pay(self, request, schedule):
        # Create order, put it and see what happens next.
        from .models import PayUOrder
        if request is not None:
            ip = request.META['REMOTE_ADDR']
        else:
            ip = '127.0.0.1'

        if request is None:
            if not self.needs_retry(schedule):
                return
            
        order = PayUOrder.objects.create(
            pos_id=self.pos_id,
            customer_ip=ip,
            schedule=schedule,
        )
        return order.put()

    def needs_retry(self, schedule):
        retry_last = schedule.payuorder_set.exclude(
            created_at=None).order_by('-created_at').first()
        if retry_last is None:
            return True

        n = now().date()
        days_since_last = (n - retry_last.created_at.date()).days

        retry_start = max(
            schedule.expires_at.date(),
            settings.CLUB_RETRIES_START
        )
        retry_days = (n - retry_start).days
        
        if retry_days > settings.CLUB_RETRY_DAYS_MAX:
            print('expired')
            return False
        if retry_days > settings.CLUB_RETRY_DAYS_DAILY:
            print('retry less often now')
            return days_since_last > settings.CLUB_RETRY_LESS
        return days_since_last > 0


class PayPal(PaymentMethod):
    slug = 'paypal'
    name = 'PayPal'
    template_name = 'club/payment/paypal.html'
    is_recurring = True
    is_onetime = False

    def invite_widget(self, schedule, request):
        return render_to_string(
            'club/payment/paypal_invite.html',
            {
                'schedule': schedule,
            },
            request=request
        )
    
    def initiate(self, request, schedule):
        app = request.GET.get('app')
        return agreement_approval_url(schedule.amount, schedule.key, app=app)

    def pay(self, request, schedule):
        from datetime import date, timedelta, datetime, timezone
        tomorrow = datetime(*(date.today() + timedelta(2)).timetuple()[:3], tzinfo=timezone.utc)
        any_active = False
        for ba in schedule.billingagreement_set.all():
            active = ba.check_agreement()
            ba.active = active
            ba.save()
            if active:
                any_active = True
        if any_active:
            schedule.expires_at = tomorrow
            schedule.save()


methods = []

pos = getattr(settings, 'CLUB_PAYU_RECURRING_POS', None)
if pos:
    recurring_payment_method = PayURe(pos)
    methods.append(recurring_payment_method)
else:
    recurring_payment_method = None

pos = getattr(settings, 'CLUB_PAYU_POS', None)
if pos:
    single_payment_method = PayU(pos)
    methods.append(single_payment_method)
else:
    single_payment_method = None



methods.append(
    PayPal()
)
