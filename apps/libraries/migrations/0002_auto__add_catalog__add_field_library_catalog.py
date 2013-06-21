# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Catalog'
        db.create_table(u'libraries_catalog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=120)),
        ))
        db.send_create_signal(u'libraries', ['Catalog'])

        # Adding field 'Library.catalog'
        db.add_column(u'libraries_library', 'catalog',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='libraries', on_delete=models.PROTECT, to=orm['libraries.Catalog']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Catalog'
        db.delete_table(u'libraries_catalog')

        # Deleting field 'Library.catalog'
        db.delete_column(u'libraries_library', 'catalog_id')


    models = {
        u'libraries.catalog': {
            'Meta': {'object_name': 'Catalog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120'})
        },
        u'libraries.library': {
            'Meta': {'object_name': 'Library'},
            'catalog': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'libraries'", 'on_delete': 'models.PROTECT', 'to': u"orm['libraries.Catalog']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'})
        }
    }

    complete_apps = ['libraries']