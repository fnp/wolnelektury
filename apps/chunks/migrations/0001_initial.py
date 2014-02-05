# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Chunk'
        db.create_table(u'chunks_chunk', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'chunks', ['Chunk'])

        # Adding model 'Attachment'
        db.create_table(u'chunks_attachment', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'chunks', ['Attachment'])


    def backwards(self, orm):
        # Deleting model 'Chunk'
        db.delete_table(u'chunks_chunk')

        # Deleting model 'Attachment'
        db.delete_table(u'chunks_attachment')


    models = {
        u'chunks.attachment': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'chunks.chunk': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Chunk'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['chunks']