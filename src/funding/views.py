# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView
from getpaid.models import Payment
from ssify import ssi_included
from ssify.utils import ssi_cache_control
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
    template_name = "funding/offer_detail.html"
    backend = 'getpaid.backends.payu'

    @csrf_exempt
    def dispatch(self, request, slug=None):
        if getattr(self, 'object', None) is None:
            if slug:
                self.object = get_object_or_404(Offer.public(), slug=slug)
            else:
                self.object = Offer.current()
                if self.object is None:
                    raise Http404
        return super(OfferDetailView, self).dispatch(request, slug)

    def get_form(self, form_class):
        if self.request.method == 'POST':
            return form_class(self.object, self.request.POST)
        else:
            return form_class(self.object, initial={'amount': app_settings.DEFAULT_AMOUNT})

    def get_context_data(self, **kwargs):
        ctx = super(OfferDetailView, self).get_context_data(**kwargs)
        ctx['object'] = self.object
        ctx['page'] = self.request.GET.get('page', 1)
        if self.object.is_current():
            ctx['funding_no_show_current'] = True
        return ctx

    def form_valid(self, form):
        funding = form.save()
        # Skip getpaid.forms.PaymentMethodForm, go directly to the broker.
        payment = Payment.create(funding, self.backend)
        gateway_url_tuple = payment.get_processor()(payment).get_gateway_url(self.request)
        payment.change_status('in_progress')
        return redirect(gateway_url_tuple[0])


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


def offer_bar(request, pk, link=False, closeable=False, show_title=True, show_title_calling=True, add_class=""):
    offer = get_object_or_404(Offer, pk=pk)
    offer_sum = offer.sum()

    return render(request, "funding/includes/funding.html", {
        'offer': offer,
        'sum': offer_sum,
        'is_current': offer.is_current(),
        'is_win': offer_sum >= offer.target,
        'missing': offer.target - offer_sum,
        'percentage': 100 * offer_sum / offer.target,
        'link': link,
        'closeable': closeable,
        'show_title': show_title,
        'show_title_calling': show_title_calling,
        'add_class': add_class,
    })


@ssi_included(patch_response=[ssi_cache_control(must_revalidate=True)])
def top_bar(request, pk):
    return offer_bar(request, pk, link=True, closeable=True, add_class="funding-top-header")


@ssi_included(patch_response=[ssi_cache_control(must_revalidate=True)])
def list_bar(request, pk):
    return offer_bar(request, pk, link=True, show_title_calling=False)


@ssi_included(patch_response=[ssi_cache_control(must_revalidate=True)])
def detail_bar(request, pk):
    return offer_bar(request, pk, show_title=False)


@ssi_included(patch_response=[ssi_cache_control(must_revalidate=True)])
def offer_status(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    return render(request, "funding/includes/offer_status.html", {'offer': offer})


@ssi_included(patch_response=[ssi_cache_control(must_revalidate=True)])
def offer_status_more(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    return render(request, "funding/includes/offer_status_more.html", {'offer': offer})


@ssi_included(patch_response=[ssi_cache_control(must_revalidate=True)])
def offer_fundings(request, pk, page):
    offer = get_object_or_404(Offer, pk=pk)
    fundings = offer.funding_payed()
    paginator = Paginator(fundings, 10, 2)
    try:
        page_obj = paginator.page(int(page))
    except InvalidPage:
        raise Http404
    return render(request, "funding/includes/fundings.html", {
        "paginator": paginator,
        "page_obj": page_obj,
        "fundings": page_obj.object_list,
    })
