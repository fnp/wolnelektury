# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models


class BillingPlan(models.Model):
    plan_id = models.CharField(max_length=32)
    amount = models.IntegerField(db_index=True, unique=True)


class BillingAgreement(models.Model):
    agreement_id = models.CharField(max_length=32)
    schedule = models.ForeignKey('club.Schedule', models.PROTECT)
    plan = models.ForeignKey(BillingPlan, models.PROTECT)
    active = models.BooleanField(max_length=32)
    token = models.CharField(max_length=32)

    def check_agreement(self):
        from .rest import check_agreement
        return check_agreement(self.agreement_id)

    def get_donations(self, year):
        from .rest import get_donations
        return get_donations(self.agreement_id, year)

    def update_donations(self, year):
        from .rest import get_donations
        for donation in get_donations(self.agreement_id, year):
            Donation.objects.get_or_create(
                transaction_id=donation['transaction_id'],
                defaults={
                    'timestamp': donation['timestamp'],
                    'amount': donation['amount'],
                }
            )


class Donation(models.Model):
    billing_agreement = models.ForeignKey(BillingAgreement, models.CASCADE)
    transaction_id = models.CharField(max_length=255, db_index=True)
    timestamp = models.DateTimeField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
