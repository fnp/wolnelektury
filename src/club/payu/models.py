# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
from urllib.parse import urlencode
from urllib.request import HTTPError
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from . import POSS


class CardToken(models.Model):
    """ This should be attached to a payment schedule. """
    pos_id = models.CharField(_('POS id'), max_length=255)
    disposable_token = models.CharField(_('disposable token'), max_length=255)
    reusable_token = models.CharField(_('reusable token'), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = _('PayU card token')
        verbose_name_plural = _('PayU card tokens')


class Order(models.Model):
    pos_id = models.CharField(_('POS id'), max_length=255)   # TODO: redundant?
    customer_ip = models.GenericIPAddressField(_('customer IP'))
    order_id = models.CharField(_('order ID'), max_length=255, blank=True)

    status = models.CharField(max_length=128, blank=True, choices=[
        ('PENDING', _('Pending')),
        ('WAITING_FOR_CONFIRMATION', _('Waiting for confirmation')),
        ('COMPLETED', _('Completed')),
        ('CANCELED', _('Canceled')),
        ('REJECTED', _('Rejected')),
    ])

    class Meta:
        abstract = True
        verbose_name = _('PayU order')
        verbose_name_plural = _('PayU orders')

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

    def status_updated(self):
        pass

    # 
    
    def get_pos(self):
        return POSS[self.pos_id]

    def get_representation(self, token=None):
        rep = {
            "notifyUrl": self.get_notify_url(),
            "customerIp": self.customer_ip,
            "merchantPosId": self.pos_id,
            "currencyCode": self.get_pos().currency_code,
            "totalAmount": str(int(self.get_amount() * 100)),
            "extOrderId": "wolne-lektury-rcz-%d" % self.pk,

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
            raise ValueError("Expecting dict with `orderId` key, got: %s" % response)
        self.order_id = response['orderId']
        self.save()

        
        return response.get('redirectUri', self.schedule.get_thanks_url())


class Notification(models.Model):
    """ Add `order` FK to real Order model. """
    body = models.TextField(_('body'))
    received_at = models.DateTimeField(_('received_at'), auto_now_add=True)

    class Meta:
        abstract = True
        verbose_name = _('PayU notification')
        verbose_name_plural = _('PayU notifications')

    def get_status(self):
        return json.loads(self.body)['order']['status']

    def apply(self):
        status = self.get_status()
        if self.order.status not in (status, 'COMPLETED'):
            self.order.status = status
            self.order.save()
            self.order.status_updated()
