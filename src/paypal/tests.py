# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.contrib.auth.models import User
from mock import MagicMock, Mock, patch, DEFAULT
from catalogue.test_utils import WLTestCase
from .models import BillingAgreement, BillingPlan
from .rest import user_is_subscribed
from paypalrestsdk import ResourceNotFound


BillingPlanMock = Mock(
    return_value=Mock(
        id='some-billing-plan-id'
    )
)

BillingAgreementMock = Mock(
    # BillingAgreement() has a .links[]
    return_value=MagicMock(
        links=[
            Mock(
                rel="approval_url",
                href="http://paypal.test/approval/"
            )
        ]
    ),
    # BillingAgreement.execute(token)
    execute=Mock(
        return_value=Mock(
            error=None,
            id='some-billing-agreement-id',
            plan=Mock(
                payment_definitions=[
                    Mock(
                        amount={'value': '100'}
                    )
                ]
            )
        )
    ),
    # Later we can BillingAgreement.find(...).state == 'Active'
    find=Mock(
        return_value=Mock(
            state='Active'
        )
    ),
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
        BillingPlan=BillingPlanMock,
        BillingAgreement=BillingAgreementMock,
    )
    def test_paypal_form_valid(self):
        """PayPal form created a BillingPlan."""
        self.client.login(username='test', password='test')
        response = self.client.post('/paypal/form/', {"amount": "100"})
        self.assertRedirects(response, 'http://paypal.test/approval/',
            fetch_redirect_response=False)
        self.assertEqual(BillingPlan.objects.all().count(), 1)

        # Posting the form a second time does not create another plan.
        response = self.client.post('/paypal/form/', {"amount": "100"})
        self.assertRedirects(response, 'http://paypal.test/approval/',
            fetch_redirect_response=False)
        self.assertEqual(BillingPlan.objects.all().count(), 1)

        # No BillingAgreement created in our DB yet.
        self.assertEqual(BillingAgreement.objects.all().count(), 0)

    @patch('paypalrestsdk.BillingPlan', BillingPlanMock)
    def test_paypal_form_error(self):
        """On PayPal error, plan does not get created."""
        self.client.login(username='test', password='test')

        # It can choke on BillingPlan().create().
        with patch('paypalrestsdk.BillingPlan', Mock(
                return_value=Mock(create=Mock(return_value=None)))):
            response = self.client.post('/paypal/form/', {"amount": "100"})
            self.assertEqual(response.status_code, 200)

        # Or it can choke on BillingPlan().activate().
        with patch('paypalrestsdk.BillingPlan', Mock(
                return_value=Mock(activate=Mock(return_value=None)))):
            response = self.client.post('/paypal/form/', {"amount": "100"})
            self.assertEqual(response.status_code, 200)

        # No plan is created yet.
        self.assertEqual(BillingPlan.objects.all().count(), 0)

        # Or it can choke later, on BillingAgreement().create()
        with patch('paypalrestsdk.BillingAgreement', Mock(
                return_value=Mock(create=Mock(return_value=None)))):
            response = self.client.post('/paypal/form/', {"amount": "100"})
            self.assertEqual(response.status_code, 200)

        # But now the plan should be created.
        self.assertEqual(BillingPlan.objects.all().count(), 1)

    @patch.multiple('paypalrestsdk',
        BillingPlan=BillingPlanMock,
        BillingAgreement=BillingAgreementMock,
    )
    def test_paypal_app_form_valid(self):
        """App form creates a BillingPlan."""
        self.client.login(username='test', password='test')
        response = self.client.post('/paypal/app-form/', {"amount": "100"})
        self.assertRedirects(response, 'http://paypal.test/approval/',
            fetch_redirect_response=False)
        self.assertEqual(BillingPlan.objects.all().count(), 1)

    @patch('paypalrestsdk.BillingAgreement', BillingAgreementMock)
    def test_paypal_return(self):
        self.client.login(username='test', password='test')
        BillingPlan.objects.create(amount=100)

        # No token = no agreement.
        response = self.client.get('/paypal/return/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(BillingAgreement.objects.all().count(), 0)

        response = self.client.get('/paypal/return/?token=secret-token')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BillingAgreement.objects.all().count(), 1)

        # Repeated returns will not generate further agreements.
        response = self.client.get('/paypal/return/?token=secret-token')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BillingAgreement.objects.all().count(), 1)

        self.assertTrue(user_is_subscribed(self.user))

    @patch('paypalrestsdk.BillingAgreement', BillingAgreementMock)
    def test_paypal_app_return(self):
        self.client.login(username='test', password='test')
        BillingPlan.objects.create(amount=100)
        response = self.client.get('/paypal/app-return/?token=secret-token')
        self.assertRedirects(
            response, 'wolnelekturyapp://paypal_return',
            fetch_redirect_response=False)

        # Repeated returns will not generate further agreements.
        response = self.client.get('/paypal/app-return/?token=secret-token')
        self.assertRedirects(
            response, 'wolnelekturyapp://paypal_return',
            fetch_redirect_response=False)
        self.assertEqual(BillingAgreement.objects.all().count(), 1)

        self.assertTrue(user_is_subscribed(self.user))

    def test_paypal_return_error(self):
        self.client.login(username='test', password='test')
        BillingPlan.objects.create(amount=100)

        # It can choke on BillingAgreement.execute()
        with patch('paypalrestsdk.BillingAgreement', Mock(
                execute=Mock(return_value=Mock(id=None)))):
            self.client.get('/paypal/app-return/?token=secret-token')
            response = self.client.get('/paypal/app-return/?token=secret-token')
            self.assertRedirects(
                response, 'wolnelekturyapp://paypal_error',
                fetch_redirect_response=False)

        # No agreement created in our DB if not executed successfully.
        self.assertEqual(BillingAgreement.objects.all().count(), 0)

        # It can execute all right, but just not be findable later.
        with patch('paypalrestsdk.BillingAgreement', Mock(
                execute=BillingAgreementMock.execute,
                find=Mock(side_effect=ResourceNotFound(None)))):
            response = self.client.get('/paypal/app-return/?token=secret-token')
            self.assertRedirects(
                response, 'wolnelekturyapp://paypal_return',
                fetch_redirect_response=False)

        # Now the agreement exists in our DB, but is not active.
        self.assertEqual([b.active for b in BillingAgreement.objects.all()], [False])

        with patch('paypalrestsdk.BillingAgreement', Mock(
                find=Mock(return_value=Mock(state='Mocked')))):
            self.assertFalse(user_is_subscribed(self.user))

    def test_paypal_cancel(self):
        response = self.client.get('/paypal/cancel/')
        self.assertEqual(response.status_code, 200)
