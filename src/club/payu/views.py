# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from hashlib import md5, sha256
from django.conf import settings
from django import http
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView, View


class Payment(TemplateView):
    pass


class RecPayment(FormView):
    """ Set form_class to a CardTokenForm. """
    template_name = 'payu/rec_payment.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        schedule = self.get_schedule()
        pos = self.get_pos()

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

        ctx['widget_args'] = widget_args
        ctx['widget_sig'] = widget_sig
        ctx['schedule'] = schedule
        ctx['pos'] = pos
        return ctx

    def form_valid(self, form):
        form.save(self)
        return super().form_valid(form)



@method_decorator(csrf_exempt, name='dispatch')
class NotifyView(View):
    """ Set `order_model` in subclass. """
    def post(self, request, pk):
        order = get_object_or_404(self.order_model, pk=pk)

        try:
            openpayu = request.META['HTTP_OPENPAYU_SIGNATURE']
            openpayu = dict(term.split('=') for term in openpayu.split(';'))
            assert openpayu['algorithm'] == 'MD5'
            assert openpayu['content'] == 'DOCUMENT'
            assert openpayu['sender'] == 'checkout'
            sig = openpayu['signature']
        except (KeyError, ValueError, AssertionError):
            return http.HttpResponseBadRequest('bad')

        document = request.body + order.get_pos().secondary_key.encode('latin1')
        if md5(document).hexdigest() != sig:
            return http.HttpResponseBadRequest('wrong')

        notification = order.notification_set.create(
            body=request.body.decode('utf-8')
        )
        notification.apply()

        return http.HttpResponse('ok')
