from django import template
from ..models import Offer

register = template.Library()


@register.inclusion_tag("funding/tags/funding.html")
def funding(offer=None, link=False, add_class=""):
    if offer is None:
        offer = Offer.current()

    return {
        'offer': offer,
        'percentage': 100 * offer.sum() / offer.target,
        'link': link,
        'add_class': add_class,
    }
