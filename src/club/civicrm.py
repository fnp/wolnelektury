from datetime import datetime
import json
from celery.task import task
from django.conf import settings
import requests
import yaml


class CiviCRM:
    def __init__(self, base, key):
        self.base = base
        self.key = key
        self.api_base = (base or '') + 'civicrm/ajax/api4/'
        self.enabled = bool(self.base and self.key)

    def request(self, resource, method, params):
        if not self.enabled:
            return

        response = requests.post(
            self.api_base + f'{resource}/{method}',
            params={
                'params': json.dumps(params),
                'api_key': self.key
            },
        )
        d = response.json()
        return d

    def create_or_update_contact(self, email, key):
        contact_id = self.get_contact_id(email)
        if contact_id is None:
            contact_id = self.create_contact(email, key)
        else:
            self.update_contact(contact_id, key)
        return contact_id

    def get_contact_id(self, email):
        result = self.request(
            'Contact',
            'get',
            {
                "join": [["Email AS email", "LEFT"]],
                "where":[["email.email", "=", email]],
                "limit":1,
                "debug":True
            }
        )['values']
        if result:
            return result[0]['id']

    def create_contact(self, email, key):
        result = self.request(
            'Contact',
            'create',
            {
                'values': {
                    'WL.TPWL_key': key,
                },
                'chain': {
                    'email': [
                        'Email',
                        'create',
                        {
                            'values': {
                                'email': email,
                                'contact_id': '$id'
                            }
                        }
                    ]
                }
            }
        )
        return result[0]['id']
    
    def update_contact(self, contact_id, key):
        return self.request(
            'Contact',
            'update',
            {
                'values': {
                    'WL.TPWL_key': key,
                },
                'where': [
                    ['id', '=', contact_id]
                ]
            }
        )
                

    def report_activity(self, email, tpwl_key, key, name, datetime, details):
        if not self.enabled:
            return

        contact_id = self.create_or_update_contact(email, tpwl_key)

        activity_id = self.get_activity_id(key)
        if activity_id is None:
            self.create_activity(
                contact_id,
                key,
                name,
                datetime,
                details
            )
        else:
            self.update_activity(
                activity_id,
                contact_id,
                name,
                datetime,
                details
            )

    def get_activity_id(self, key):
        result = self.request(
            'Activity',
            'get',
            {
                'where': [
                    ['subject', '=', key],
                ]
            }
        )['values']
        if result:
            return result[0]['id']
    
    def create_activity(self, contact_id, key, name, date_time, details):
        detail_str = yaml.dump(details)
        return self.request(
            'Activity',
            'create',
            {
                'values': {
                    'source_contact_id': contact_id,
                    'activity_type_id:name': name,
                    'status_id:name': 'Completed',
                    'activity_date_time': date_time.isoformat() if date_time else '',
                    'details' : detail_str,
                    'subject': key,
                },
                'debug': True,
            }
        )

    def update_activity(self, activity_id, contact_id, name, date_time, details):
        detail_str = yaml.dump(details)

        self.request(
            'Activity',
            'update',
            {
                'values': {
                    'source_contact_id': contact_id,
                    'activity_type_id:name': name,
                    'status_id:name': 'Completed',
                    'activity_date_time': date_time.isoformat(),
                    'details' : detail_str,
                },
                'where': [
                    ['id', '=', activity_id]
                ]
            }
        )
    
    #do we create a civicontribution?


civicrm = CiviCRM(
    settings.CIVICRM_BASE,
    settings.CIVICRM_KEY,
)

@task(ignore_result=True)
def report_activity(*args, **kwargs):
    civicrm.report_activity(*args, **kwargs)


