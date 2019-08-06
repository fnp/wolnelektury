# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import requests


class POS:
    ACCESS_TOKEN_URL = '/pl/standard/user/oauth/authorize'
    API_BASE = '/api/v2_1/'

    def __init__(self, pos_id, client_secret, secondary_key, sandbox=False, currency_code='PLN'):
        self.pos_id = pos_id
        self.client_secret = client_secret
        self.secondary_key = secondary_key
        self.sandbox = sandbox
        self.currency_code = currency_code

    def get_api_host(self):
        if self.sandbox:
            return 'https://secure.snd.payu.com'
        else:
            return 'https://secure.payu.com'

    def get_access_token(self):
        response = requests.post(
            self.get_api_host() + self.ACCESS_TOKEN_URL,
            data={
                'grant_type': 'client_credentials',
                'client_id': self.pos_id,
                'client_secret': self.client_secret
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data['token_type'] == 'bearer'
        assert data['grant_type'] == 'client_credentials'
        return data['access_token']

    def request(self, method, url, data):
        access_token = self.get_access_token()

        full_url = self.get_api_host() + self.API_BASE + url
        response = requests.request(
            method, full_url, json=data, headers={
                'Authorization': 'Bearer ' + access_token,
            },
            allow_redirects=False
        )
        return response.json()

