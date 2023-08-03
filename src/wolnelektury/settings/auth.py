# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # 'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2
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
        # 'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        # 'INIT_PARAMS': {'cookie': True},
        # 'FIELDS': [
        #     'id',
        #     'email',
        #     'name',
        #     'first_name',
        #     'last_name',
        #     'verified',
        #     'locale',
        #     'timezone',
        #     'link',
        #     'gender',
        #     'updated_time',
        # ],
        # 'EXCHANGE_TOKEN': True,
        # 'LOCALE_FUNC': 'path.to.callable',
        # 'VERIFIED_EMAIL': False,
        'VERSION': 'v2.12',
    },
}
