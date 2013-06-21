# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Library.slug'
        db.add_column(u'libraries_library', 'slug',
                      self.gf('django.db.models.fields.SlugField')(max_length=120, unique=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Library.slug'
        db.delete_column(u'libraries_library', 'slug')


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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'unique': 'True', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'})
        }
    }

    complete_apps = ['libraries']