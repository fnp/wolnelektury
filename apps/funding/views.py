# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, FormView, DetailView
from .forms import DummyForm
from .models import Offer, Spent


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
        for o in Offer.objects.all():
            if o.state() == 'lose':
                o.wlfund = o.sum()
                if o.wlfund > 0:
                    offers.append(o)
            elif o.state() == 'win':
                o.wlfund = o.sum() - o.target
                if o.wlfund > 0:
                    offers.append(o)
        amount = sum(o.wlfund for o in offers) - sum(o.amount for o in Spent.objects.all())
        print offers

        ctx['amount'] = amount
        ctx['log'] = add_total(amount, mix(
            (offers, lambda x: x.end, 'offer'),
            (Spent.objects.all(), lambda x: x.timestamp, 'spent'),
        ))
        return ctx


class OfferDetailView(FormView):
    form_class = DummyForm
    template_name = "funding/offer_detail.html"

    def dispatch(self, request, slug):
        self.object = get_object_or_404(Offer.public(), slug=slug)
        return super(OfferDetailView, self).dispatch(request, slug)

    def get_form(self, form_class):
        if self.request.method == 'POST':
            return form_class(self.object, self.request.POST)
        else:
            return form_class(self.object, initial={'amount': settings.FUNDING_DEFAULT})

    def get_context_data(self, *args, **kwargs):
        ctx = super(OfferDetailView, self).get_context_data(*args, **kwargs)
        ctx['object'] = self.object
        return ctx

    def form_valid(self, form):
        form.save()
        return redirect(reverse("funding_thanks"))


class ThanksView(TemplateView):
    template_name = "funding/thanks.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super(ThanksView, self).get_context_data(*args, **kwargs)
        ctx['object'] = Offer.current()
        return ctx
