# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sponsor'
        db.create_table(u'sponsors_sponsor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('_description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'sponsors', ['Sponsor'])

        # Adding model 'SponsorPage'
        db.create_table(u'sponsors_sponsorpage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('sponsors', self.gf('jsonfield.fields.JSONField')(default='{}')),
            ('_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('sprite', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'sponsors', ['SponsorPage'])


    def backwards(self, orm):
        # Deleting model 'Sponsor'
        db.delete_table(u'sponsors_sponsor')

        # Deleting model 'SponsorPage'
        db.delete_table(u'sponsors_sponsorpage')


    models = {
        u'sponsors.sponsor': {
            'Meta': {'object_name': 'Sponsor'},
            '_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'sponsors.sponsorpage': {
            'Meta': {'object_name': 'SponsorPage'},
            '_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'sponsors': ('jsonfield.fields.JSONField', [], {'default': "'{}'"}),
            'sprite': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['sponsors']