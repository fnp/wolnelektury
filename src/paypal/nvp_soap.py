# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
# UNUSED
import requests
import urlparse
from django.conf import settings

DESC = 'Wolne Lektury subscription'


def paypal_request(data):
    request_data = {
        'USER': settings.PAYPAL['user'],
        'PWD': settings.PAYPAL['password'],
        'SIGNATURE': settings.PAYPAL['signature'],
        'SUBJECT': settings.PAYPAL['email'],
        'VERSION': 93,
    }
    request_data.update(data)

    response = requests.post(settings.PAYPAL['api-url'], data=request_data)
    return dict(urlparse.parse_qsl(response.text))


def set_express_checkout(amount):
    response = paypal_request({
        'METHOD': 'SetExpressCheckout',
        'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE',
        'PAYMENTREQUEST_0_AMT': amount,
        'PAYMENTREQUEST_0_CURRENCYCODE': 'PLN',
        'L_BILLINGTYPE0': 'RecurringPayments',
        'L_BILLINGAGREEMENTDESCRIPTION0': DESC,
        'RETURNURL': settings.PAYPAL['return-url'],
        'CANCELURL': settings.PAYPAL['cancel-url'],
    })
    return response.get('TOKEN')


def create_profile(token, amount):
    response = paypal_request({
        'METHOD': 'CreateRecurringPaymentsProfile',
        'TOKEN': token,
        'PROFILESTARTDATE': '2011-03-11T00:00:00Z',
        'DESC': DESC,
        'MAXFAILEDPAYMENTS': 3,
        'AUTOBILLAMT': 'AddToNextBilling',
        'BILLINGPERIOD': 'Month',  # or 30 Days?
        'BILLINGFREQUENCY': 1,
        'AMT': amount,
        'CURRENCYCODE': 'PLN',
        'L_PAYMENTREQUEST_0_ITEMCATEGORY0': 'Digital',
        'L_PAYMENTREQUEST_0_NAME0': 'Subskrypcja Wolnych Lektur',
        'L_PAYMENTREQUEST_0_AMT0': amount,
        'L_PAYMENTREQUEST_0_QTY0': 1,
    })
    return response.get('PROFILEID')


# min amount: 10, max amount: 30000
