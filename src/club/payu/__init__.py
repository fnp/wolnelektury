from django.conf import settings
from .pos import POS


POSS = {
    k: POS(k, **v)
    for (k, v) in settings.PAYU_POS.items()
}
