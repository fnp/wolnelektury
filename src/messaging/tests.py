from datetime import datetime
from django.test import TestCase
from django.utils.timezone import make_aware
from club.models import Schedule
from .models import Contact
from . import states

#    Cold,
#    ClubTried,
#    ClubSingle,
#    ClubSingleExpired,
#    ClubRecurring,
#    ClubRecurringExpired,
###  ClubRecurringCancelled


class MessagingTests(TestCase):
    def test_tried(self):
        # user1 has one unsuccessful try.
        Schedule.objects.create(email='user1@example.com', amount=1)
        
        # user2 has one unsuccessful and one successful try
        Schedule.objects.create(email='user2@example.com', amount=1)
        Schedule.objects.create(
            email='user2@example.com', amount=1,
            payed_at=make_aware(datetime(2020, 1, 1)),
            expires_at=make_aware(datetime(2030, 2, 1)),
        )

        state = states.ClubTried()
        self.assertEqual(
            [c.email for c in state.get_contacts()],
            ['user1@example.com']
        )

    def test_single_and_recurring(self):
        # This user has both single and recurring payments.
        Schedule.objects.create(
            email='user1@example.com', amount=1,
            payed_at=make_aware(datetime(2020, 1, 1)),
            expires_at=make_aware(datetime(2030, 2, 1)),
        )
        Schedule.objects.create(
            email='user1@example.com', amount=1,
            payed_at=make_aware(datetime(2020, 1, 1)),
            expires_at=make_aware(datetime(2030, 2, 1)),
            monthly=True
        )
        self.assertEqual(
            [c.email for c in states.ClubSingle().get_contacts()],
            []
        )
        self.assertEqual(
            [c.email for c in states.ClubRecurring().get_contacts()],
            ['user1@example.com']
        )

    def test_recurring_expired(self):
        # User1 has expiring
        Schedule.objects.create(
            email='user1@example.com', amount=1,
            payed_at=make_aware(datetime(2020, 1, 1)),
            expires_at=make_aware(datetime(2020, 2, 1)),
            monthly=True
        )

        Schedule.objects.create(
            email='user2@example.com', amount=1,
            payed_at=make_aware(datetime(2020, 1, 1)),
            expires_at=make_aware(datetime(2020, 2, 1)),
            monthly=True,
            is_cancelled=True,
        )

        self.assertEqual(
            [c.email for c in states.ClubRecurringExpired().get_contacts()],
            ['user1@example.com', 'user2@example.com']
        )

# Start -> 


        
# Has recurring-cancelled AND single
