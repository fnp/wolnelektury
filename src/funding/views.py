# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView
import club.payu.views
from . import app_settings
from .forms import FundingForm
from .models import Offer, Spent, Funding


def mix(*streams):
    substreams = []
    for stream, read_date, tag in streams:
        iterstream = iter(stream)
        try:
            item = next(iterstream)
        except StopIteration:
            pass
        else:
            substreams.append([read_date(item), item, iterstream, read_date, tag])
    while substreams:
        i, substream = max(enumerate(substreams), key=lambda x: x[1][0])
        yield substream[4], substream[1]
        try:
            item = next(substream[2])
        except StopIteration:
            del substreams[i]
        else:
            substream[0:2] = [substream[3](item), item]


class WLFundView(TemplateView):
    template_name = "funding/wlfund.html"

    def get_context_data(self):
        def add_total(total, it):
            for tag, e in it:
                e.total = total
                if tag == 'spent':
                    total += e.amount
                else:
                    total -= e.wlfund
                yield tag, e

        ctx = super(WLFundView, self).get_context_data()
        offers = []

        for o in Offer.past():
            if o.is_win():
                o.wlfund = o.sum() - o.target
                if o.wlfund > 0:
                    offers.append(o)
            else:
                o.wlfund = o.sum()
                if o.wlfund > 0:
                    offers.append(o)
        amount = sum(o.wlfund for o in offers) - sum(o.amount for o in Spent.objects.all())

        ctx['amount'] = amount
        ctx['log'] = add_total(amount, mix(
            (offers, lambda x: x.end, 'offer'),
            (Spent.objects.all().select_related(), lambda x: x.timestamp, 'spent'),
        ))
        return ctx


class OfferDetailView(FormView):
    form_class = FundingForm
    template_name = 'funding/2022/offer_detail.html'

    @csrf_exempt
    def dispatch(self, request, slug=None):
        if getattr(self, 'object', None) is None:
            if slug:
                if request.user.is_staff:
                    offers = Offer.objects.all()
                else:
                    offers = Offer.public()
                self.object = get_object_or_404(offers, slug=slug)
            else:
                self.object = Offer.current()
                if self.object is None:
                    raise Http404
        return super(OfferDetailView, self).dispatch(request, slug)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        if self.request.method == 'POST':
            return form_class(self.request, self.object, self.request.POST)
        else:
            return form_class(self.request, self.object, initial={'amount': app_settings.DEFAULT_AMOUNT})

    def get_context_data(self, **kwargs):
        ctx = super(OfferDetailView, self).get_context_data(**kwargs)
        ctx['object'] = self.object
        if self.object.is_current():
            ctx['funding_no_show_current'] = True
        return ctx

    def form_valid(self, form):
        funding = form.save()
        return redirect(funding.put())


class CurrentView(OfferDetailView):
    @csrf_exempt
    def dispatch(self, request, slug=None):
        self.object = Offer.current()
        if self.object is None:
            return redirect(reverse('funding'))
        elif slug != self.object.slug:
            return redirect(reverse('funding_current', args=[self.object.slug]))
        return super(CurrentView, self).dispatch(request, slug)


class OfferListView(ListView):
    queryset = Offer.public()
    template_name = 'funding/2022/offer_list.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(OfferListView, self).get_context_data(**kwargs)
        ctx['funding_no_show_current'] = True
        return ctx


class ThanksView(TemplateView):
    template_name = "funding/thanks.html"

    def get_context_data(self, **kwargs):
        ctx = super(ThanksView, self).get_context_data(**kwargs)
        ctx['offer'] = Offer.current()
        ctx['funding_no_show_current'] = True
        return ctx


class NoThanksView(TemplateView):
    template_name = "funding/no_thanks.html"


class DisableNotifications(TemplateView):
    template_name = "funding/disable_notifications.html"

    @csrf_exempt
    def dispatch(self, request):
        self.object = get_object_or_404(Funding, email=request.GET.get('email'), notify_key=request.GET.get('key'))
        return super(DisableNotifications, self).dispatch(request)

    def post(self, *args, **kwargs):
        self.object.disable_notifications()
        return redirect(self.request.get_full_path())


@login_required
def claim(request, key):
    funding = get_object_or_404(Funding, notify_key=key)
    if funding.user is None:
        funding.user = request.user
        funding.save()
    return HttpResponseRedirect(
        funding.offer.book.get_absolute_url() if funding.offer.book is not None
        else funding.offer.get_absolute_url()
    )


class PayUNotifyView(club.payu.views.NotifyView):
    order_model = Funding

