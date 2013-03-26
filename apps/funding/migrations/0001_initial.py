# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Offer'
        db.create_table('funding_offer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('book_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('redakcja_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('target', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('funding', ['Offer'])

        # Adding model 'Perk'
        db.create_table('funding_perk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['funding.Offer'], null=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('funding', ['Perk'])

        # Adding model 'Funding'
        db.create_table('funding_funding', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['funding.Offer'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('payed_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('funding', ['Funding'])

        # Adding M2M table for field perks on 'Funding'
        db.create_table('funding_funding_perks', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('funding', models.ForeignKey(orm['funding.funding'], null=False)),
            ('perk', models.ForeignKey(orm['funding.perk'], null=False))
        ))
        db.create_unique('funding_funding_perks', ['funding_id', 'perk_id'])


    def backwards(self, orm):
        # Deleting model 'Offer'
        db.delete_table('funding_offer')

        # Deleting model 'Perk'
        db.delete_table('funding_perk')

        # Deleting model 'Funding'
        db.delete_table('funding_funding')

        # Removing M2M table for field perks on 'Funding'
        db.delete_table('funding_funding_perks')


    models = {
        'funding.funding': {
            'Meta': {'ordering': "['-payed_at']", 'object_name': 'Funding'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['funding.Offer']"}),
            'payed_at': ('django.db.models.fields.DateTimeField', [], {}),
            'perks': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['funding.Perk']", 'symmetrical': 'False'})
        },
        'funding.offer': {
            'Meta': {'ordering': "['-end']", 'object_name': 'Offer'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'book_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redakcja_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'target': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'funding.perk': {
            'Meta': {'ordering': "['-price']", 'object_name': 'Perk'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['funding.Offer']", 'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['funding']