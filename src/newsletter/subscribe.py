# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import requests


def subscribe(email, newsletter):
    list_id = newsletter.phplist_id
    data = {
        "email": email,
        "emailconfirm": email,
        f"list[{list_id}]": "signup",
        "htmlemail": 1,
        "subscribe": "Subscribe",
    }
    response = requests.post(
        'https://mailing.mdrn.pl/?p=subscribe',
        data=data,
    )
    response.raise_for_status()

