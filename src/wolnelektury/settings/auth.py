# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2
LOGIN_URL = '/uzytkownik/login/'

LOGIN_REDIRECT_URL = '/'

SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_QUERY_EMAIL = True


SOCIALACCOUNT_PROVIDERS = {
    'openid': {
        'SERVERS': [{
            'id': 'google',
            'name': 'Google',
            'openid_url': 'https://www.google.com/accounts/o8/id'}],
    },
}
