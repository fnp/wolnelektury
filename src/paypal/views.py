# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect

from api.utils import HttpResponseAppRedirect
from club.models import Schedule
from paypal.rest import execute_agreement, check_agreement, agreement_approval_url
from paypal.models import BillingAgreement, BillingPlan


def paypal_init(request, key):
    schedule = get_object_or_404(Schedule, key=key)
    schedule.method = 'paypal'
    schedule.save(update_fields=['method'])
    app = request.GET.get('app')
    return redirect(agreement_approval_url(schedule.amount, schedule.key, app=app))


@login_required
def paypal_return(request, key, app=False):
    schedule = get_object_or_404(Schedule, key=key)
    
    token = request.GET.get('token')
    if not token:
        raise Http404
    if not BillingAgreement.objects.filter(token=token):
        resource = execute_agreement(token)
        if resource.id:
            amount = int(Decimal(resource.plan.payment_definitions[0].amount['value']))
            plan = BillingPlan.objects.get(amount=amount)
            active = check_agreement(resource.id) or False
            BillingAgreement.objects.create(
                agreement_id=resource.id, schedule=schedule, plan=plan, active=active, token=token)
            if active:
                schedule.set_payed()
    else:
        resource = None
    if app:
        if getattr(resource, 'error', None):
            return HttpResponseAppRedirect('wolnelekturyapp://paypal_error')
        else:
            return HttpResponseAppRedirect('wolnelekturyapp://paypal_return')
    else:
        return HttpResponseRedirect(schedule.get_thanks_url())


def paypal_cancel(request):
    return render(request, 'paypal/cancel.html', {})
