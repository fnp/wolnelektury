# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Chunk.content_fr'
        db.alter_column(u'chunks_chunk', 'content_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_ru'
        db.alter_column(u'chunks_chunk', 'content_ru', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_es'
        db.alter_column(u'chunks_chunk', 'content_es', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_it'
        db.alter_column(u'chunks_chunk', 'content_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_uk'
        db.alter_column(u'chunks_chunk', 'content_uk', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_de'
        db.alter_column(u'chunks_chunk', 'content_de', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_lt'
        db.alter_column(u'chunks_chunk', 'content_lt', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_pl'
        db.alter_column(u'chunks_chunk', 'content_pl', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_en'
        db.alter_column(u'chunks_chunk', 'content_en', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Chunk.content_fr'
        db.alter_column(u'chunks_chunk', 'content_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_ru'
        db.alter_column(u'chunks_chunk', 'content_ru', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_es'
        db.alter_column(u'chunks_chunk', 'content_es', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_it'
        db.alter_column(u'chunks_chunk', 'content_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_uk'
        db.alter_column(u'chunks_chunk', 'content_uk', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_de'
        db.alter_column(u'chunks_chunk', 'content_de', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_lt'
        db.alter_column(u'chunks_chunk', 'content_lt', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_pl'
        db.alter_column(u'chunks_chunk', 'content_pl', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Chunk.content_en'
        db.alter_column(u'chunks_chunk', 'content_en', self.gf('django.db.models.fields.TextField')(null=True))

    models = {
        u'chunks.attachment': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'chunks.chunk': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Chunk'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_lt': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_pl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_ru': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_uk': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['chunks']