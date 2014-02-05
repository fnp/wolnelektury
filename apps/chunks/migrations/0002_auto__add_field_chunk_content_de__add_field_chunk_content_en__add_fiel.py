# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Chunk.content_de'
        db.add_column(u'chunks_chunk', 'content_de',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_en'
        db.add_column(u'chunks_chunk', 'content_en',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_es'
        db.add_column(u'chunks_chunk', 'content_es',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_fr'
        db.add_column(u'chunks_chunk', 'content_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_it'
        db.add_column(u'chunks_chunk', 'content_it',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_lt'
        db.add_column(u'chunks_chunk', 'content_lt',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_pl'
        db.add_column(u'chunks_chunk', 'content_pl',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_ru'
        db.add_column(u'chunks_chunk', 'content_ru',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Chunk.content_uk'
        db.add_column(u'chunks_chunk', 'content_uk',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Chunk.content_de'
        db.delete_column(u'chunks_chunk', 'content_de')

        # Deleting field 'Chunk.content_en'
        db.delete_column(u'chunks_chunk', 'content_en')

        # Deleting field 'Chunk.content_es'
        db.delete_column(u'chunks_chunk', 'content_es')

        # Deleting field 'Chunk.content_fr'
        db.delete_column(u'chunks_chunk', 'content_fr')

        # Deleting field 'Chunk.content_it'
        db.delete_column(u'chunks_chunk', 'content_it')

        # Deleting field 'Chunk.content_lt'
        db.delete_column(u'chunks_chunk', 'content_lt')

        # Deleting field 'Chunk.content_pl'
        db.delete_column(u'chunks_chunk', 'content_pl')

        # Deleting field 'Chunk.content_ru'
        db.delete_column(u'chunks_chunk', 'content_ru')

        # Deleting field 'Chunk.content_uk'
        db.delete_column(u'chunks_chunk', 'content_uk')


    models = {
        u'chunks.attachment': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'chunks.chunk': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Chunk'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_it': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'content_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        }
    }

    complete_apps = ['chunks']