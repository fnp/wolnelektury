# Create your views here.
from django.views.generic import TemplateView
from .models import Offer


def mix(*streams):
    substreams = []
    for stream, read_date in streams:
        iterstream = iter(stream)
        try:
            item = next(iterstream)
        except StopIteration:
            pass
        else:
            substreams.append([read_date(item), item, iterstream, read_date])
    while substreams:
        i, substream = max(enumerate(substreams), key=lambda x: x[0])
        yield substream[1]
        try:
            item = next(substream[2])
        except StopIteration:
            del substreams[i]
        else:
            substream[0:2] = [substream[3](item), item]


class WLFundView(TemplateView):
    template_name = "funding/wlfund.html"

    def get_context_data(self):
        ctx = super(WLFundView, self).get_context_data()
        offers = [o for o in Offer.objects.all() if o.state() == 'lose' and o.sum()]
        amount = sum(o.sum() for o in offers)
        print offers

        #offers = (o for o in Offer.objects.all() if o.state() == 'lose' and o.sum())
        ctx['amount'] = amount
        ctx['log'] = mix((offers, lambda x: x.end))
        return ctx
