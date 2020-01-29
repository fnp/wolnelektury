from datetime import timedelta
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from .recipient import Recipient


class State:
    allow_negative_offset = False
    context_fields = []


    def __init__(self, time=None, min_days_since=None, max_days_since=None):
        self.time = time or now()
        self.min_days_since = min_days_since
        self.max_days_since = max_days_since

    def get_recipients(self):
        return [
            self.get_recipient(obj)
            for obj in self.get_objects()
        ]

    def get_recipient(self, obj):
        return Recipient(
                hash_value=self.get_hash_value(obj),
                email=self.get_email(obj),
                context=self.get_context(obj),
            )

    def get_example_recipient(self, email):
        return self.get_recipient(
                self.get_example_object(email)
            )

    def get_example_object(self, email):
        from club.models import Schedule
        n = now()
        return Schedule(
                email=email,
                key='xxxxxxxxx',
                amount=100,
                payed_at=n - timedelta(2),
                started_at=n - timedelta(1),
                expires_at=n + timedelta(1),
            )

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


class ClubSingle(State):
    slug = 'club-single'
    name = _('club one-time donors')


class ClubSingleExpired(State):
    slug = 'club-membership-expiring'
    allow_negative_offset = True
    name = _('club one-time donors with donation expiring')

    def get_objects(self):
        from club.models import Schedule
        return Schedule.objects.filter(
                is_active=True,
                expires_at__lt=self.time - self.offset
            )

    def get_hashed_value(self, obj):
        return '%s:%s' % (obj.pk, obj.expires_at.isoformat())


class ClubTried(State):
    slug = 'club-payment-unfinished'
    name = _('club would-be donors')

    def get_objects(self):
        from club.models import Schedule
        return Schedule.objects.filter(
                payuorder=None,
                started_at__lt=self.time - self.offset,
            )


class ClubRecurring(State):
    slug = 'club-recurring'
    name = _('club recurring donors')


class ClubRecurringExpired(State):
    slug = 'club-recurring-payment-problem'
    name = _('club recurring donors with donation expired')

    def get_objects(self):
        from club.models import Schedule
        return Schedule.objects.none()


class Cold(State):
    slug = 'cold'
    name = _('cold group')


states = [
    Cold,
    ClubTried,
    ClubSingle,
    ClubSingleExpired,
    ClubRecurring,
    ClubRecurringExpired,
]

