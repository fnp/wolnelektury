# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Picture.gazeta_link'
        db.delete_column(u'picture_picture', 'gazeta_link')

        # Adding field 'Picture.culturepl_link'
        db.add_column(u'picture_picture', 'culturepl_link',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=240, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Picture.gazeta_link'
        db.add_column(u'picture_picture', 'gazeta_link',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=240, blank=True),
                      keep_default=False)

        # Deleting field 'Picture.culturepl_link'
        db.delete_column(u'picture_picture', 'culturepl_link')


    models = {
        u'picture.picture': {
            'Meta': {'ordering': "('sort_key',)", 'object_name': 'Picture'},
            'areas': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'culturepl_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'extra_info': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['picture']