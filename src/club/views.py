from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import FormView, CreateView, TemplateView, DetailView, UpdateView
from django.views import View
from .payu import POSS
from .payu import views as payu_views
from .forms import ScheduleForm, PayUCardTokenForm
from . import models
from .helpers import get_active_schedule
from .payment_methods import payure_method


class ClubView(TemplateView):
    template_name = 'club/index.html'


class JoinView(CreateView):
    form_class = ScheduleForm
    template_name = 'club/membership_form.html'

    def is_app(self):
        return self.request.GET.get('app')

    def get(self, request):
        if self.is_app():
            request.session['from_app'] = True
        elif request.session and 'from_app' in request.session:
            del request.session['from_app']
        schedule = get_active_schedule(request.user)
        if schedule is not None:
            return HttpResponseRedirect(schedule.get_absolute_url())
        else:
            return super(JoinView, self).get(request)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, form=None):
        c = super(JoinView, self).get_context_data()
        c['membership'] = getattr(self.request.user, 'membership', None)
        return c

    def get_initial(self):
        if self.request.user.is_authenticated and self.request.user.email:
            return {
                'email': self.request.user.email,
            }

    def form_valid(self, form):
        retval = super(JoinView, self).form_valid(form)
        if self.request.user.is_authenticated:
            form.instance.membership, created = models.Membership.objects.get_or_create(user=self.request.user)
            form.instance.save()
        return retval

    def get_success_url(self):
        return self.object.initiate_payment(self.request)


class ScheduleView(DetailView):
    model = models.Schedule
    slug_field = slug_url_kwarg = 'key'
    template_name = 'club/schedule.html'

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


class PayUPayment(payu_views.Payment):
    pass


class PayURecPayment(payu_views.RecPayment):
    form_class = PayUCardTokenForm

    def get_schedule(self):
        return get_object_or_404(models.Schedule, key=self.kwargs['key'])

    def get_pos(self):
        pos_id = payure_method.pos_id
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
