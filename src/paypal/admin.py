from django.contrib import admin
from . import models


admin.site.register(models.BillingAgreement)
admin.site.register(models.BillingPlan)

