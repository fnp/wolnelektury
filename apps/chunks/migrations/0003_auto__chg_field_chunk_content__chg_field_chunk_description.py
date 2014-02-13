# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Chunk.content'
        db.alter_column(u'chunks_chunk', 'content', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.description'
        db.alter_column(u'chunks_chunk', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):

        # Changing field 'Chunk.content'
        db.alter_column(u'chunks_chunk', 'content', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Chunk.description'
        db.alter_column(u'chunks_chunk', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    models = {
        u'chunks.attachment': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'chunks.chunk': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Chunk'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_it': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['chunks']