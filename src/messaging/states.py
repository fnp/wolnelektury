from datetime import timedelta
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from .recipient import Recipient


class State:
    allow_negative_offset = False
    context_fields = []


    def __init__(self, offset=0, time=None):
        self.time = time or now()
        if isinstance(offset, int):
            offset = timedelta(offset)
        self.offset = offset

    def get_recipients(self):
        return [
            Recipient(
                hash_value=self.get_hash_value(obj),
                email=self.get_email(obj),
                context=self.get_context(obj),
            )
            for obj in self.get_objects()
        ]

    def get_objects(self):
        raise NotImplemented

    def get_hash_value(self, obj):
        return str(obj.pk)
    
    def get_email(self, obj):
        return obj.email

    def get_context(self, obj):
        ctx = {
            obj._meta.model_name: obj,
        }
        return ctx


class ClubMembershipExpiring(State):
    slug = 'club-membership-expiring'
    allow_negative_offset = True
    name = _('club membership expiring')

    def get_objects(self):
        from club.models import Schedule
        return Schedule.objects.filter(
                is_active=True,
                expires_at__lt=self.time - self.offset
            )

    def get_hashed_value(self, obj):
        return '%s:%s' % (obj.pk, obj.expires_at.isoformat())


class ClubPaymentUnfinished(State):
    slug = 'club-payment-unfinished'
    name = _('club payment unfinished')

    def get_objects(self):
        from club.models import Schedule
        return Schedule.objects.filter(
                payuorder=None,
                started_at__lt=self.time - self.offset,
            )


class ClubRecurringPaymentProblem(State):
    slug = 'club-recurring-payment-problem'
    name = _('club recurring payment problem')

    def get_objects(self):
        from club.models import Schedule
        return Schedule.objects.none()


states = [
    ClubMembershipExpiring,
    ClubPaymentUnfinished,
    ClubRecurringPaymentProblem,
]

