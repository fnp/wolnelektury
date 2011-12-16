# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'InfoPage.page_title'
        db.delete_column('infopages_infopage', 'page_title')

        # Deleting field 'InfoPage.page_title_en'
        db.delete_column('infopages_infopage', 'page_title_en')

        # Deleting field 'InfoPage.page_title_es'
        db.delete_column('infopages_infopage', 'page_title_es')

        # Deleting field 'InfoPage.page_title_fr'
        db.delete_column('infopages_infopage', 'page_title_fr')

        # Deleting field 'InfoPage.page_title_uk'
        db.delete_column('infopages_infopage', 'page_title_uk')

        # Deleting field 'InfoPage.page_title_de'
        db.delete_column('infopages_infopage', 'page_title_de')

        # Deleting field 'InfoPage.page_title_lt'
        db.delete_column('infopages_infopage', 'page_title_lt')

        # Deleting field 'InfoPage.page_title_pl'
        db.delete_column('infopages_infopage', 'page_title_pl')

        # Deleting field 'InfoPage.page_title_ru'
        db.delete_column('infopages_infopage', 'page_title_ru')

        # Adding field 'InfoPage.main_page'
        db.add_column('infopages_infopage', 'main_page', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'InfoPage.page_title'
        db.add_column('infopages_infopage', 'page_title', self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_en'
        db.add_column('infopages_infopage', 'page_title_en', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_es'
        db.add_column('infopages_infopage', 'page_title_es', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_fr'
        db.add_column('infopages_infopage', 'page_title_fr', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_uk'
        db.add_column('infopages_infopage', 'page_title_uk', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_de'
        db.add_column('infopages_infopage', 'page_title_de', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_lt'
        db.add_column('infopages_infopage', 'page_title_lt', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_pl'
        db.add_column('infopages_infopage', 'page_title_pl', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Adding field 'InfoPage.page_title_ru'
        db.add_column('infopages_infopage', 'page_title_ru', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True), keep_default=False)

        # Deleting field 'InfoPage.main_page'
        db.delete_column('infopages_infopage', 'main_page')


    models = {
        'infopages.infopage': {
            'Meta': {'ordering': "('main_page', 'slug')", 'object_name': 'InfoPage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_column': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'left_column_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'left_column_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
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
            'title_lt': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_pl': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True}),
            'title_uk': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': True, 'blank': True})
        }
    }

    complete_apps = ['infopages']
