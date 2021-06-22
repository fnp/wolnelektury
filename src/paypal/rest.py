# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import timedelta

import paypalrestsdk
import pytz
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from .models import BillingPlan, BillingAgreement

paypalrestsdk.configure(settings.PAYPAL_CONFIG)


class PaypalError(Exception):
    pass


def absolute_url(url_name, kwargs=None):
    return "http://%s%s" % (Site.objects.get_current().domain, reverse(url_name, kwargs=kwargs))


def create_plan(amount):
    billing_plan = paypalrestsdk.BillingPlan({
        "name": "Cykliczna darowizna na Wolne Lektury: %s zł" % amount,
        "description": "Cykliczna darowizna na wsparcie Wolnych Lektur",
        "merchant_preferences": {
            "auto_bill_amount": "yes",
            "return_url": absolute_url('paypal_return', {'key': '-'}),
            "cancel_url": absolute_url('paypal_cancel'),
            # "initial_fail_amount_action": "continue",
            "max_fail_attempts": "3",
        },
        "payment_definitions": [
            {
                "amount": {
                    "currency": "PLN",
                    "value": str(amount),
                },
                "cycles": "0",
                "frequency": "MONTH",
                "frequency_interval": "1",
                "name": "Cykliczna darowizna",
                "type": "REGULAR",
            }
        ],
        "type": "INFINITE",
    })

    if not billing_plan.create():
        raise PaypalError(billing_plan.error)
    if not billing_plan.activate():
        raise PaypalError(billing_plan.error)
    plan, created = BillingPlan.objects.get_or_create(amount=amount, defaults={'plan_id': billing_plan.id})
    return plan.plan_id


def get_link(links, rel):
    for link in links:
        if link.rel == rel:
            return link.href


def create_agreement(amount, key, app=False):
    try:
        plan = BillingPlan.objects.get(amount=amount)
    except BillingPlan.DoesNotExist:
        plan_id = create_plan(amount)
    else:
        plan_id = plan.plan_id
    start = (timezone.now() + timedelta(0, 3600*24)).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    billing_agreement = paypalrestsdk.BillingAgreement({
        "name": "Subskrypcja klubu WL",
        "description": "Stałe wsparcie Wolnych Lektur kwotą %s złotych" % amount,
        "start_date": start,
        "plan": {
            "id": plan_id,
        },
        "payer": {
            "payment_method": "paypal"
        },
    })
    if app:
        billing_agreement['override_merchant_preferences'] = {
            'return_url': absolute_url('paypal_app_return', {'key': key}),
        }
    else:
        billing_agreement['override_merchant_preferences'] = {
            'return_url': absolute_url('paypal_return', {'key': key}),
        }
        

    response = billing_agreement.create()
    if response:
        return billing_agreement
    else:
        raise PaypalError(billing_agreement.error)


def agreement_approval_url(amount, key, app=False):
    agreement = create_agreement(amount, key, app=app)
    return get_link(agreement.links, 'approval_url')


def get_agreement(agreement_id):
    try:
        return paypalrestsdk.BillingAgreement.find(agreement_id)
    except paypalrestsdk.ResourceNotFound:
        return None


def check_agreement(agreement_id):
    a = get_agreement(agreement_id)
    if a:
        return a.state == 'Active'


def user_is_subscribed(user):
    agreements = BillingAgreement.objects.filter(user=user)
    return any(agreement.check_agreement() for agreement in agreements)


def execute_agreement(token):
    return paypalrestsdk.BillingAgreement.execute(token)
