# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import timedelta

import paypalrestsdk
import pytz
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils import timezone
from paypalrestsdk import BillingPlan, BillingAgreement, ResourceNotFound
from django.conf import settings
from .models import BillingPlan as BillingPlanModel

paypalrestsdk.configure(settings.PAYPAL_CONFIG)


class PaypalError(Exception):
    pass


def absolute_url(url_name):
    return "http://%s%s" % (Site.objects.get_current().domain, reverse(url_name))


def create_plan(amount):
    billing_plan = BillingPlan({
        "name": "Cykliczna darowizna na Wolne Lektury: %s zł" % amount,
        "description": "Cykliczna darowizna na wsparcie Wolnych Lektur",
        "merchant_preferences": {
            "auto_bill_amount": "yes",
            "return_url": absolute_url('paypal_return'),
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
    plan, created = BillingPlanModel.objects.get_or_create(amount=amount, defaults={'plan_id': billing_plan.id})
    return plan.plan_id


def get_link(links, rel):
    for link in links:
        if link.rel == rel:
            return link.href


def create_agreement(amount):
    try:
        plan = BillingPlanModel.objects.get(amount=amount)
    except BillingPlanModel.DoesNotExist:
        plan_id = create_plan(amount)
    else:
        plan_id = plan.plan_id
    start = (timezone.now() + timedelta(0, 3600*24)).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    billing_agreement = BillingAgreement({
        "name": u"Subskrypcja klubu WL",
        "description": u"Stałe wsparcie Wolnych Lektur kwotą %s złotych" % amount,
        "start_date": start,
        "plan": {
            "id": plan_id,
        },
        "payer": {
            "payment_method": "paypal"
        },
    })

    response = billing_agreement.create()
    if response:
        return billing_agreement
    else:
        raise PaypalError(billing_agreement.error)


def agreement_approval_url(amount):
    agreement = create_agreement(amount)
    return get_link(agreement.links, 'approval_url')


def get_agreement(agreement_id):
    try:
        return BillingAgreement.find(agreement_id)
    except ResourceNotFound:
        return None


def check_agreement(agreement_id):
    a = get_agreement(agreement_id)
    if a:
        return a.state == 'Active'


def execute_agreement(token):
    return BillingAgreement.execute(token)
