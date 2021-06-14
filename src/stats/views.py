from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum
from . import forms
from . import models


class TopView(PermissionRequiredMixin, TemplateView):
    model = models.Visits
    permission_required = 'stats.view_visits'
    template_name = 'stats/top.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = forms.VisitsForm(self.request.GET)
        assert form.is_valid()
        visits = self.model.objects.all()
        if form.cleaned_data['date_since']:
            visits = visits.filter(date__gte=form.cleaned_data['date_since'].replace(day=1))
        if form.cleaned_data['date_until']:
            visits = visits.filter(date__lte=form.cleaned_data['date_until'])
        visits = visits.values('book__slug').annotate(
            views=Sum('views'),
            unique_views=Sum('unique_views')
        )
        visits = visits.order_by('-unique_views')
        ctx['form'] = form
        ctx['visits'] = visits
        return ctx


class DailyTopView(TopView):
    model = models.DayVisits
