# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from django.conf import settings
from shutil import move
from os import path


def move_sponsors_media(orm, old, new):
    move(path.join(settings.MEDIA_ROOT, old), 
        path.join(settings.MEDIA_ROOT, new))
    for sponsor in orm.Sponsor.objects.all():
        base, rest = sponsor.logo.name.split('/', 1)
        sponsor.logo.name = '/'.join((new, rest))
        sponsor.save()
    # reset cache
    for sponsor_page in orm.SponsorPage.objects.all():
        sponsor_page.save()
    

class Migration(DataMigration):
    
    def forwards(self, orm):
        "Write your forwards methods here."
        if not db.dry_run:
            move_sponsors_media(orm, 'sponsors', 'sponsorzy')
    
    def backwards(self, orm):
        "Write your backwards methods here."
        if not db.dry_run:
            move_sponsors_media(orm, 'sponsorzy', 'sponsors')
    
    
    models = {
        'sponsors.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            '_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'sponsors.sponsorpage': {
            'Meta': {'object_name': 'SponsorPage'},
            '_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'sponsors': ('sponsors.fields.JSONField', [], {'default': '{}'})
        }
    }
    
    complete_apps = ['sponsors']
