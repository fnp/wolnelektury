from django.conf import settings
from django.db import models


KEY_SIZE = 18
SECRET_SIZE = 32

CONSUMER_STATES = (
    ('pending', 'Pending approval'),
    ('accepted', 'Accepted'),
    ('canceled', 'Canceled'),
)


class Nonce(models.Model):
    token_key = models.CharField(max_length=KEY_SIZE)
    consumer_key = models.CharField(max_length=KEY_SIZE)
    key = models.CharField(max_length=255)

    def __unicode__(self):
        return u"Nonce %s for %s" % (self.key, self.consumer_key)


class Resource(models.Model):
    name = models.CharField(max_length=255)
    url = models.TextField(max_length=2047)
    is_readonly = models.BooleanField(default=True)


class Consumer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    status = models.CharField(max_length=16, choices=CONSUMER_STATES, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='consumers')

    def __unicode__(self):
        return u"Consumer %s with key %s" % (self.name, self.key)


class Token(models.Model):
    REQUEST = 1
    ACCESS = 2
    TOKEN_TYPES = ((REQUEST, u'Request'), (ACCESS, u'Access'))

    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    token_type = models.IntegerField(choices=TOKEN_TYPES)
    timestamp = models.IntegerField()
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='tokens')
    consumer = models.ForeignKey(Consumer)

    def __unicode__(self):
        return u"%s Token %s for %s" % (self.get_token_type_display(), self.key, self.consumer)
