from django.views.generic import TemplateView


class MainSwitchView(TemplateView):
    template_name = 'experiments/main_switch.html'
