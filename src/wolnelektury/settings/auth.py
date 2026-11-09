# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
AUTHENTICATION_BACKENDS = [
    #'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
FEATURE_CONFIRM_USER = False

LOGIN_URL = '/uzytkownik/login/'

LOGIN_REDIRECT_URL = '/'

SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_QUERY_EMAIL = True


SOCIALACCOUNT_PROVIDERS = {
    'openid': {
        'SERVERS': [],
    },
    'google': {
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
    },
}
