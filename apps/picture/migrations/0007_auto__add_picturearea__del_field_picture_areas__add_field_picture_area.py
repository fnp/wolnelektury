# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PictureArea'
        db.create_table(u'picture_picturearea', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='areas', to=orm['picture.Picture'])),
            ('area', self.gf('jsonfield.fields.JSONField')(default={})),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=10, db_index=True)),
        ))
        db.send_create_signal(u'picture', ['PictureArea'])

        # Deleting field 'Picture.areas'
        db.delete_column(u'picture_picture', 'areas')

        # Adding field 'Picture.areas_json'
        db.add_column(u'picture_picture', 'areas_json',
                      self.gf('jsonfield.fields.JSONField')(default={}),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'PictureArea'
        db.delete_table(u'picture_picturearea')

        # Adding field 'Picture.areas'
        db.add_column(u'picture_picture', 'areas',
                      self.gf('jsonfield.fields.JSONField')(default={}),
                      keep_default=False)

        # Deleting field 'Picture.areas_json'
        db.delete_column(u'picture_picture', 'areas_json')


    models = {
        u'picture.picture': {
            'Meta': {'ordering': "('sort_key',)", 'object_name': 'Picture'},
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