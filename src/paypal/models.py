# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models


class BillingPlan(models.Model):
    plan_id = models.CharField(max_length=32)
    amount = models.IntegerField(db_index=True, unique=True)


class BillingAgreement(models.Model):
    agreement_id = models.CharField(max_length=32)
    user = models.ForeignKey(User)
    plan = models.ForeignKey(BillingPlan)
    active = models.BooleanField(max_length=32)
    token = models.CharField(max_length=32)

    def check_agreement(self):
        from .rest import check_agreement
        return check_agreement(self.agreement_id)
