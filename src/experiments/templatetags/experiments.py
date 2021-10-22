from django.conf import settings
from django.template import Library


register = Library()


@register.inclusion_tag('experiments/switch.html', takes_context=True)
def experiments_switcher(context):
    tests = []
    explicit = False
    for exp in settings.EXPERIMENTS:
        currval = context['request'].EXPERIMENTS.get(exp['slug'])
        if exp.get('switchable') or context.get('EXPERIMENTS_SWITCHABLE_' + test['slug']):
            tests.append((exp, currval))
            for cohort in exp.get('cohorts'):
                if cohort.get('explicit') and cohort.get('value') == currval:
                    explicit = True
    return {
        'tests': tests,
        'explicit': explicit,
    }
