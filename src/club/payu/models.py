# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import json
from urllib.parse import urlencode
from urllib.request import HTTPError
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from . import POSS


class CardToken(models.Model):
    """ This should be attached to a payment schedule. """
    pos_id = models.CharField('POS id', max_length=255)
    disposable_token = models.CharField('token jednorazowy', max_length=255)
    reusable_token = models.CharField('token wielokrotnego użytku', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField('utworzony', auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = 'token PayU karty płatniczej'
        verbose_name_plural = 'tokeny PayU kart płatniczych'


class Order(models.Model):
    pos_id = models.CharField('POS id', max_length=255)   # TODO: redundant?
    customer_ip = models.GenericIPAddressField('adres IP klienta')
    order_id = models.CharField('ID zamówienia', max_length=255, blank=True)

    status = models.CharField(max_length=128, blank=True, choices=[
        ('PENDING', 'Czeka'),
        ('WAITING_FOR_CONFIRMATION', 'Czeka na potwierdzenie'),
        ('COMPLETED', 'Ukończone'),
        ('CANCELED', 'Anulowane'),
        ('REJECTED', 'Odrzucone'),

        ('ERR-INVALID_TOKEN', 'Błędny token'),
    ])
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = 'Zamówienie PayU'
        verbose_name_plural = 'Zamówienia PayU'

    # These need to be provided in a subclass.

    def get_amount(self):
        raise NotImplementedError()

    def get_buyer(self):
        raise NotImplementedError()

    def get_continue_url(self):
        raise NotImplementedError()
    
    def get_description(self):
        raise NotImplementedError()

    def get_products(self):
        """ At least: name, unitPrice, quantity. """
        return [
            {
                'name': self.get_description(),
                'unitPrice': str(int(self.get_amount() * 100)),
                'quantity': '1',
            },
        ]

    def is_recurring(self):
        return False

    def get_notify_url(self):
        raise NotImplementedError

    def get_thanks_url(self):
        raise NotImplementedError

    def status_updated(self):
        pass

    # 
    
    def get_pos(self):
        return POSS[self.pos_id]

    def get_continue_url(self):
        return "https://{}{}".format(
            Site.objects.get_current().domain,
            self.get_thanks_url())

    def get_representation(self, token=None):
        rep = {
            "notifyUrl": self.get_notify_url(),
            "customerIp": self.customer_ip,
            "merchantPosId": self.pos_id,
            "currencyCode": self.get_pos().currency_code,
            "totalAmount": str(int(self.get_amount() * 100)),
            "extOrderId": "wolne-lektury-%d" % self.pk,

            "buyer": self.get_buyer() or {},
            "continueUrl": self.get_continue_url(),
            "description": self.get_description(),
            "products": self.get_products(),
        }
        if token:
            token = self.get_card_token()
            rep['recurring'] = 'STANDARD' if token.reusable_token else 'FIRST'
            rep['payMethods'] = {
                "payMethod": {
                    "type": "CARD_TOKEN",
                    "value": token.reusable_token or token.disposable_token
                }
            }
        return rep

    def put(self):
        token = self.get_card_token() if self.is_recurring() else None
        representation = self.get_representation(token)
        try:
            response = self.get_pos().request('POST', 'orders', representation)
        except HTTPError as e:
            resp = json.loads(e.read().decode('utf-8'))
            if resp['status']['statusCode'] == 'ERROR_ORDER_NOT_UNIQUE':
                pass
            else:
                raise

        if token:
            reusable_token = response.get('payMethods', {}).get('payMethod', {}).get('value', None)
            if reusable_token:
                token.reusable_token = reusable_token
                token.save()
            # else?

        if 'orderId' not in response:
            code = response.get('status', {}).get('codeLiteral', '')
            if code:
                self.status = 'ERR-' + str(code)
                self.save()
                self.status_updated()
            else:
                raise ValueError("Expecting dict with `orderId` key, got: %s" % response)
        else:
            self.order_id = response['orderId']
            self.save()

        return response.get('redirectUri', self.get_thanks_url())


class Notification(models.Model):
    """ Add `order` FK to real Order model. """
    body = models.TextField('treść')
    received_at = models.DateTimeField('odebrana', auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = 'notyfikacja PayU'
        verbose_name_plural = 'notyfikacje PayU'

    def get_status(self):
        return json.loads(self.body)['order']['status']

    def apply(self):
        status = self.get_status()
        if self.order.status not in (status, 'COMPLETED'):
            self.order.status = status
            if status == 'COMPLETED':
                self.order.completed_at = now()
            self.order.save()
            self.order.status_updated()
