# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings

cred = credentials.Certificate(settings.FCM_PRIVATE_KEY_PATH)
firebase_admin.initialize_app(cred)

TOPIC = 'wolnelektury'


def send_fcm_push(title, body, image_url=None):
    # See documentation on defining a message payload.
    data = {}
    # data = {
    #     'title': title,
    #     'body': body,
    # }
    if image_url:
        data['imageUrl'] = image_url
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data,
        topic=TOPIC,
    )
    message_id = messaging.send(message)
    return message_id
