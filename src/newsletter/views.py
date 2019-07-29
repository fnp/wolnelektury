from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from newsletter.forms import UnsubscribeForm, SubscribeForm
from newsletter.models import Subscription


def subscribe_form(request):
    if request.POST:
        form = SubscribeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('subscribed'))
    else:
        form = SubscribeForm()
    return render(request, 'newsletter/subscribe_form.html', {
        'page_title': _(u'Subscribe To Newsletter'),
        'form': form,
    })


def subscribed(request):
    return render(request, 'newsletter/subscribed.html', {
        'page_title': _(u'Subscribed'),
    })


def check_subscription(subscription, hashcode):
    if hashcode != subscription.hashcode():
        raise Http404


def confirm_subscription(request, subscription_id, hashcode):
    subscription = get_object_or_404(Subscription, id=subscription_id)
    check_subscription(subscription, hashcode)
    subscription.active = True
    subscription.save()
    return render(request, 'newsletter/confirm_subscription.html', {
        'page_title': _(u'Subscription confirmed')
    })


def unsubscribe_form(request):
    if request.POST:
        form = UnsubscribeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('unsubscribed'))
    else:
        form = UnsubscribeForm()
    return render(request, 'newsletter/unsubscribe_form.html', {
        'page_title': _(u'Unsubscribe'),
        'form': form,
    })


def unsubscribed(request):
    return render(request, 'newsletter/unsubscribed.html', {
        'page_title': _(u'Unsubscribed'),
    })
