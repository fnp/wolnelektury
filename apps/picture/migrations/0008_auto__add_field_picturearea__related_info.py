# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Picture._related_info'
        db.add_column(u'picture_picture', '_related_info',
                      self.gf('jsonfield.fields.JSONField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Picture._related_info'
        db.delete_column(u'picture_picture', '_related_info')


    models = {
        u'picture.picture': {
            'Meta': {'ordering': "('sort_key',)", 'object_name': 'Picture'},
            '_related_info': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'areas_json': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'culturepl_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'extra_info': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        u'picture.picturearea': {
            'Meta': {'object_name': 'PictureArea'},
            'area': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'areas'", 'to': u"orm['picture.Picture']"})
        }
    }

    complete_apps = ['picture']