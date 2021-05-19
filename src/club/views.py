# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, CreateView, TemplateView, DetailView, UpdateView
from django.views import View
from .payu import POSS
from .payu import views as payu_views
from .forms import ScheduleForm, PayUCardTokenForm
from . import models
from .helpers import get_active_schedule
from .payment_methods import recurring_payment_method


class ClubView(TemplateView):
    template_name = 'club/index.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['active_menu_item'] = 'club'
        return ctx


class JoinView(CreateView):
    form_class = ScheduleForm
    template_name = 'club/membership_form.html'

    def is_app(self):
        return self.request.GET.get('app')

    def get(self, request):
        # TODO: configure as app-allowed hosts.
        if settings.CLUB_APP_HOST and self.is_app() and request.META['HTTP_HOST'] != settings.CLUB_APP_HOST:
            return HttpResponseRedirect("https://" + settings.CLUB_APP_HOST + request.get_full_path())

        if self.is_app():
            request.session['from_app'] = True
        elif request.session and 'from_app' in request.session:
            del request.session['from_app']
        return super(JoinView, self).get(request)

    def get_context_data(self, **kwargs):
        c = super(JoinView, self).get_context_data(**kwargs)
        c['membership'] = getattr(self.request.user, 'membership', None)
        c['active_menu_item'] = 'club'
        c['club'] = models.Club.objects.first()

        c['ambassador'] = models.Ambassador.objects.all().order_by('?').first()
        return c

    def get_initial(self):
        if self.request.user.is_authenticated and self.request.user.email:
            return {
                'email': self.request.user.email,
            }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['referer'] = self.request.META.get('HTTP_REFERER', '')
        return kwargs

    def form_valid(self, form):
        retval = super(JoinView, self).form_valid(form)
        if self.request.user.is_authenticated:
            form.instance.membership, created = models.Membership.objects.get_or_create(user=self.request.user)
            form.instance.save()
        return retval

    def get_success_url(self):
        return self.object.initiate_payment(self.request)


@method_decorator(never_cache, name='dispatch')
class ScheduleView(DetailView):
    model = models.Schedule
    slug_field = slug_url_kwarg = 'key'
    template_name = 'club/schedule.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['active_menu_item'] = 'club'
        return ctx

    def post(self, request, key):
        schedule = self.get_object()
        return HttpResponseRedirect(schedule.initiate_payment(request))


@login_required
def claim(request, key):
    schedule = models.Schedule.objects.get(key=key, membership=None)
    schedule.membership, created = models.Membership.objects.get_or_create(user=request.user)
    schedule.save()
    return HttpResponseRedirect(schedule.get_absolute_url())


def cancel(request, key):
    schedule = models.Schedule.objects.get(key=key)
    schedule.is_cancelled = True
    schedule.save()
    return HttpResponseRedirect(schedule.get_absolute_url())


class DummyPaymentView(TemplateView):
    template_name = 'club/dummy_payment.html'

    def get_context_data(self, key):
        return {
            'schedule': models.Schedule.objects.get(key=key),
        }

    def post(self, request, key):
        schedule = models.Schedule.objects.get(key=key)
        schedule.create_payment()
        return HttpResponseRedirect(schedule.get_absolute_url())


class PayUPayment(DetailView):
    model = models.Schedule
    slug_field = slug_url_kwarg = 'key'

    def get(self, request, key):
        schedule = self.get_object()
        return HttpResponseRedirect(schedule.initiate_payment(request))



class PayURecPayment(payu_views.RecPayment):
    form_class = PayUCardTokenForm

    def get_schedule(self):
        return get_object_or_404(models.Schedule, key=self.kwargs['key'])

    def get_pos(self):
        pos_id = recurring_payment_method.pos_id
        return POSS[pos_id]

    def get_success_url(self):
        return self.get_schedule().pay(self.request)


class PayUNotifyView(payu_views.NotifyView):
    order_model = models.PayUOrder


class MembershipView(UpdateView):
    fields = ['name']

    def get_success_url(self):
        # TODO: get only current schedule if multiple.
        return self.object.schedule_set.first().get_absolute_url()

    def get_object(self):
        return self.request.user.membership


class ScheduleThanksView(DetailView):
    model = models.Schedule
    slug_field = slug_url_kwarg = 'key'
    template_name = 'club/thanks.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['active_menu_item'] = 'club'
        return ctx


class YearSummaryView(DetailView):
    model = models.Schedule
    slug_field = slug_url_kwarg = 'key'
    template_name = 'club/year_summary.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['payments'] = models.PayUOrder.objects.filter(
            status='COMPLETED',
            completed_at__year=self.kwargs['year'],
            schedule__email=self.object.email,
        ).order_by('completed_at')
        ctx['total_amount'] = ctx['payments'].aggregate(s=Sum('schedule__amount'))['s']
        return ctx
