from django.views.generic import TemplateView


class MainSwitchView(TemplateView):
    template_name = 'experiments/main_switch.html'

    def get_context_data(self):
        return {
            'experiments': [
                e for e in self.request.EXPERIMENTS.values()
                if e.switchable or self.request.user.is_staff
            ]
        }
