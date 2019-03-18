from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView, CreateView, TemplateView
from django.views import View
from .forms import ScheduleForm
from . import models
from .helpers import get_active_schedule


class ClubView(TemplateView):
    template_name = 'club/index.html'


class JoinView(CreateView):
    form_class = ScheduleForm
    template_name = 'club/membership_form.html'

    def get(self, request):
        schedule = get_active_schedule(request.user)
        if schedule is not None:
            return HttpResponseRedirect(schedule.get_absolute_url())
        else:
            return super(JoinView, self).get(request)

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


class AppJoinView(JoinView):
    template_name = 'club/membership_form_app.html'


class ScheduleView(View):
    def get(self, request, key):
        schedule = models.Schedule.objects.get(key=key)
        if not schedule.is_active:
            return HttpResponseRedirect(schedule.get_payment_method().get_payment_url(schedule))
        else:
            return render(
                request,
                'club/schedule.html',
                {
                    'schedule': schedule,
                }
            )


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
