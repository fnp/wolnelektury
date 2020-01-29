from datetime import timedelta
from django.apps import apps
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


class Level:
    COLD = 10
    TRIED = 20
    SINGLE = 30
    RECURRING = 40
    OPT_OUT = 50


class State:
    allow_negative_offset = False
    level = None
    expired = None

    def __init__(self, time=None, min_days_since=None, max_days_since=None, test=False):
        self.time = time or now()
        self.min_days_since = min_days_since
        self.max_days_since = max_days_since
        self.test = test

    def get_contacts(self):
        Contact = apps.get_model('messaging', 'Contact')
        contacts = Contact.objects.filter(level=self.level)

        if self.min_days_since is not None or self.expired:
            cutoff = self.time - timedelta(self.min_days_since or 0)
            if self.expired:
                contacts = contacts.filter(expires_at__lt=cutoff)
            else:
                contacts = contacts.filter(since__lt=cutoff)

        if self.max_days_since is not None:
            cutoff = self.time - timedelta(self.max_days_since)
            if self.expired:
                contacts = contacts.filter(expires_at__gt=cutoff)
            else:
                contacts = contacts.filter(since__gt=cutoff)

        if self.expired is False:
            contacts = contacts.exclude(expires_at__lt=self.time)

        return contacts

    def get_context(self, contact):
        if self.test:
            return self.get_example_context(contact)

        Schedule = apps.get_model('club', 'Schedule')
        schedules = Schedule.objects.filter(email=contact.email)
        return {
            "schedule": self.get_schedule(schedules)
        }

    def get_example_context(self, contact):
        Schedule = apps.get_model('club', 'Schedule')
        return {
            "schedule": Schedule(
                email=contact.email,
                key='xxxxxxxxx',
                amount=100,
                payed_at=self.time - timedelta(2),
                started_at=self.time - timedelta(1),
                expires_at=self.time + timedelta(1),
            )
        }


class ClubSingle(State):
    slug = 'club-single'
    name = _('club one-time donors')
    level = Level.SINGLE
    expired = False

    def get_schedule(self, schedules):
        # Find first single non-expired schedule.
        return schedules.filter(
            monthly=False, yearly=False,
            expires_at__gt=self.time
        ).order_by('started_at').first()


class ClubSingleExpired(State):
    slug = 'club-membership-expiring'
    allow_negative_offset = True
    name = _('club one-time donors with donation expiring')
    level = Level.SINGLE
    expired = True

    def get_schedule(self, schedules):
        # Find last single expired schedule.
        return schedules.filter(
            monthly=False, yearly=False,
            expires_at__lt=self.time
        ).order_by('-expires_at').first()


class ClubTried(State):
    slug = 'club-payment-unfinished'
    name = _('club would-be donors')
    level = Level.TRIED

    def get_schedule(self, schedules):
        # Find last unpaid schedule.
        return schedules.filter(
            payed_at=None
        ).order_by('-started_at').first()


class ClubRecurring(State):
    slug = 'club-recurring'
    name = _('club recurring donors')
    level = Level.RECURRING
    expired = False

    def get_schedule(self, schedules):
        # Find first recurring non-expired schedule.
        return schedules.exclude(
            monthly=False, yearly=False
        ).filter(
            expires_at__gt=self.time
        ).order_by('started_at').first()


class ClubRecurringExpired(State):
    slug = 'club-recurring-payment-problem'
    name = _('club recurring donors with donation expired')
    level = Level.RECURRING
    expired = True

    def get_schedule(self, schedules):
        # Find last recurring expired schedule.
        return schedules.exclude(
            monthly=False, yearly=False
        ).filter(
            expires_at__lt=self.time
        ).order_by('-expires_at').first()


class Cold(State):
    slug = 'cold'
    name = _('cold group')
    level = Level.COLD

    def get_context(self, contact):
        return {}


states = [
    Cold,
    ClubTried,
    ClubSingle,
    ClubSingleExpired,
    ClubRecurring,
    ClubRecurringExpired,
]

