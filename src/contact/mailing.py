# -*- coding: utf-8 -*-

from hashlib import md5

import requests
from django.conf import settings
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

INTERESTS = {settings.MAILCHIMP_GROUP_ID: True}


def get_client():
    headers = requests.utils.default_headers()
    headers['User-Agent'] = '%s (%s)' % settings.MANAGERS[0]


def subscriber_hash(email):
    return md5(email).hexdigest()


def remove_from_groups(email, client):
    group_ids = []
    categories = client.lists.interest_categories.all(list_id=settings.MAILCHIMP_LIST_ID)['categories']
    for category in categories:
        groups = client.lists.interest_categories.interests.all(
            list_id=settings.MAILCHIMP_LIST_ID, category_id=category['id'])['interests']
        group_ids += [group['id'] for group in groups]
    interests = {group_id: False for group_id in group_ids}
    client.lists.members.update(
         settings.MAILCHIMP_LIST_ID, subscriber_hash(email),
         data={'interests': interests})


def subscribe(email):
    client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY, timeout=10.0)
    try:
        member = client.lists.members.get(settings.MAILCHIMP_LIST_ID, subscriber_hash(email))
    except MailChimpError:
        pass
    else:
        if member['status'] != 'subscribed':
            remove_from_groups(email, client)
    client.lists.members.create_or_update(
        settings.MAILCHIMP_LIST_ID, subscriber_hash(email),
        data={
            'email_address': email,
            'status_if_new': 'subscribed',
            'status': 'subscribed',
            'interests': INTERESTS,
        }
    )
