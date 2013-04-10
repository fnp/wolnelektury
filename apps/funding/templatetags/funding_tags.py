from django import template
from ..models import Offer

register = template.Library()


@register.inclusion_tag("funding/tags/funding.html", takes_context=True)
def funding(context, offer=None, link=False, add_class=""):
    if offer is None and context.get('funding_no_show_current') is None:
        offer = Offer.current()
    if offer is None:
        return {}

    offer_sum = offer.sum()
    return {
        'offer': offer,
        'sum': offer_sum,
        'is_current': offer.is_current(),
        'missing': offer.target - offer_sum,
        'percentage': 100 * offer_sum / offer.target,
        'link': link,
        'add_class': add_class,
    }


@register.inclusion_tag("funding/tags/offer_detail_head.html")
def offer_detail_head(offer):
    return {
        'offer': offer,
        'state': offer.state(),
    }
    
