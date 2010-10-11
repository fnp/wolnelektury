# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'SponsorPage.sprite'
        db.add_column('sponsors_sponsorpage', 'sprite', self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'SponsorPage.sprite'
        db.delete_column('sponsors_sponsorpage', 'sprite')


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
            'sponsors': ('sponsors.fields.JSONField', [], {'default': '{}'}),
            'sprite': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['sponsors']
