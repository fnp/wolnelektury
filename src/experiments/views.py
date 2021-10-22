from django.views.generic import TemplateView
from django.conf import settings


class MainSwitchView(TemplateView):
    template_name = 'experiments/main_switch.html'

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['experiments'] = [
            {
                "config": conf,
                "value": self.request.EXPERIMENTS.get(conf['slug'])
            }
            for conf in settings.EXPERIMENTS
        ]
        return ctx
