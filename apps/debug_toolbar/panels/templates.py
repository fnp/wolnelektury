from debug_toolbar.panels import DebugPanel
from django.conf import settings
from django.dispatch import dispatcher
from django.core.signals import request_started
from django.test.signals import template_rendered
from django.template.loader import render_to_string

# Based on http://www.djangosnippets.org/snippets/766/
from django.test.utils import instrumented_test_render
from django.template import Template, Context
if Template.render != instrumented_test_render:
    Template.original_render = Template.render
    Template.render = instrumented_test_render
# MONSTER monkey-patch
old_template_init = Template.__init__
def new_template_init(self, template_string, origin=None, name='<Unknown Template>'):
    old_template_init(self, template_string, origin, name)
    self.origin = origin
Template.__init__ = new_template_init

class TemplatesDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing the request.
    """
    name = 'Templates'
    
    def __init__(self, *args, **kwargs):
        super(TemplatesDebugPanel, self).__init__(*args, **kwargs)
        self.templates_used = []
        self.contexts_used = []
        template_rendered.connect(self._storeRenderedTemplates)
        
    def _storeRenderedTemplates(self, **kwargs):
        template = kwargs.pop('template')
        if template:
            self.templates_used.append(template)
        context = kwargs.pop('context')
        if context:
            self.contexts_used.append(context)

    def process_response(self, request, response):
        self.templates = [
            (t.name, t.origin and t.origin.name or 'No origin')
            for t in self.templates_used
        ]
        return response

    def title(self):
        return 'Templates: %.2fms'

    def url(self):
        return ''

    def content(self):
        context = {
            'templates': self.templates,
            'template_dirs': settings.TEMPLATE_DIRS,
        }
        
        return render_to_string('debug_toolbar/panels/templates.html', context)