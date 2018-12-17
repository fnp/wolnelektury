# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from mock import Mock, patch, DEFAULT
from catalogue.test_utils import WLTestCase
from .models import BillingPlan


BillingAgreementMock = Mock(
    execute=Mock(
        return_value=Mock(
            plan=Mock(
                payment_definitions=[
                    Mock(
                        amount={'value': '100'}
                    )
                ]
            )
        )
    )
)


class PaypalTests(WLTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User(username='test')
        cls.user.set_password('test')
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_paypal_form(self):
        response = self.client.get('/paypal/form/')
        self.assertEqual(response.status_code, 200)

    def test_paypal_form_unauthorized(self):
        """Legacy flow: only allow payment for logged-in users."""
        response = self.client.post('/paypal/form/', {"amount": "0"})
        self.assertEqual(response.status_code, 403)

    def test_paypal_form_invalid(self):
        """Paypal form: error on bad input."""
        self.client.login(username='test', password='test')

        response = self.client.post('/paypal/form/', {"amount": "0"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['form'].errors['amount']),
            1)

    @patch.multiple('paypalrestsdk',
        BillingPlan=DEFAULT,
        BillingAgreement=DEFAULT
    )
    def test_paypal_form_valid(self, BillingPlan, BillingAgreement):
        self.client.login(username='test', password='test')
        response = self.client.post('/paypal/form/', {"amount": "100"})
        self.assertEqual(response.status_code, 302)
        # Assert: BillingPlan created? BillingAgreement created?
        # Models created?

    @patch.multiple('paypalrestsdk',
        BillingPlan=DEFAULT,
        BillingAgreement=DEFAULT,
    )
    def test_paypal_form_valid(self, BillingPlan, BillingAgreement):
        self.client.login(username='test', password='test')
        response = self.client.post('/paypal/app-form/', {"amount": "100"})
        self.assertEqual(response.status_code, 302)

    @patch.multiple('paypalrestsdk',
        BillingAgreement=BillingAgreementMock
    )
    def test_paypal_return(self):
        self.client.login(username='test', password='test')
        BillingPlan.objects.create(amount=100)
        response = self.client.get('/paypal/return/?token=secret-token')

    def test_paypal_cancel(self):
        response = self.client.get('/paypal/cancel/')
        self.assertEqual(response.status_code, 200)
