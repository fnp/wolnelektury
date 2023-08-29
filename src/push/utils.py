# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings


cred = None
if hasattr(settings, 'FCM_PRIVATE_KEY_PATH'):
    cred = credentials.Certificate(settings.FCM_PRIVATE_KEY_PATH)
    firebase_admin.initialize_app(cred)

TOPIC = 'wolnelektury'


def send_fcm_push(title, body, image_url=None):
    if cred is None:
        return
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
