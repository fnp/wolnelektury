from django import template
from ..models import Offer

register = template.Library()


@register.inclusion_tag("funding/tags/funding.html")
def funding(offer=None, link=False, add_class=""):
    if offer is None:
        offer = Offer.current()
    if offer is None:
        return {}

    return {
        'offer': offer,
        'is_current': offer.is_current(),
        'percentage': 100 * offer.sum() / offer.target,
        'link': link,
        'add_class': add_class,
    }


@register.inclusion_tag("funding/tags/offer_detail_head.html")
def offer_detail_head(offer):
    return {
        'offer': offer,
        'state': offer.state(),
    }
    
