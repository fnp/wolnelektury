# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'InfoPage.left_column_jp'
        db.delete_column('infopages_infopage', 'left_column_jp')

        # Deleting field 'InfoPage.title_jp'
        db.delete_column('infopages_infopage', 'title_jp')

        # Deleting field 'InfoPage.right_column_jp'
        db.delete_column('infopages_infopage', 'right_column_jp')


    def backwards(self, orm):
        
        # Adding field 'InfoPage.left_column_jp'
        db.add_column('infopages_infopage', 'left_column_jp', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.title_jp'
        db.add_column('infopages_infopage', 'title_jp', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.right_column_jp'
        db.add_column('infopages_infopage', 'right_column_jp', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)


    models = {
        'infopages.infopage': {
            'Meta': {'ordering': "('main_page', 'slug')", 'object_name': 'InfoPage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_column': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'left_column_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_it': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'main_page': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'right_column': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'right_column_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_it': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'right_column_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_es': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_lt': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_pl': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_uk': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True})
        }
    }

    complete_apps = ['infopages']
