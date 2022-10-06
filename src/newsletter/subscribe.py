# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import requests
from django.conf import settings
from club.civicrm import civicrm


def subscribe(email, newsletter):
    if newsletter.crm_id:
        subscribe_crm(email, newsletter.crm_id)
    if newsletter.phplist_id:
        subscribe_phplist(email, newsletter.phplist_id)

def subscribe_crm(email, group_id):
    civicrm.add_email_to_group(email, group_id)

def subscribe_phplist(email, list_id):
    data = {
        "email": email,
        "emailconfirm": email,
        f"list[{list_id}]": "signup",
        "htmlemail": 1,
        "subscribe": "Subscribe",
    }
    if settings.NEWSLETTER_PHPLIST_SUBSCRIBE_URL:
        response = requests.post(
            settings.NEWSLETTER_PHPLIST_SUBSCRIBE_URL,
            data=data,
        )
        response.raise_for_status()
    else:
        print("Newsletter not configured, "
            "NEWSLETTER_PHPLIST_SUBSCRIBE_URL not set. "
            f"Trying to subscribe email: {email} to newsletter: {list_id}."
        )
