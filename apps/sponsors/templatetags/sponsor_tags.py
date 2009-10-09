from django import template

from sponsors import models


register = template.Library()


def sponsors():
    return {'sponsor_groups': models.SponsorGroup.objects.all()}
    
compressed_js = register.inclusion_tag('sponsors/sponsors.html')(sponsors)
