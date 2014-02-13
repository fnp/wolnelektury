# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'InfoPage.title_de'
        db.alter_column(u'infopages_infopage', 'title_de', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.left_column_uk'
        db.alter_column(u'infopages_infopage', 'left_column_uk', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_pl'
        db.alter_column(u'infopages_infopage', 'right_column_pl', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_lt'
        db.alter_column(u'infopages_infopage', 'right_column_lt', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_lt'
        db.alter_column(u'infopages_infopage', 'left_column_lt', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_ru'
        db.alter_column(u'infopages_infopage', 'right_column_ru', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_fr'
        db.alter_column(u'infopages_infopage', 'left_column_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_lt'
        db.alter_column(u'infopages_infopage', 'title_lt', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_es'
        db.alter_column(u'infopages_infopage', 'right_column_es', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_fr'
        db.alter_column(u'infopages_infopage', 'title_fr', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_en'
        db.alter_column(u'infopages_infopage', 'right_column_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_de'
        db.alter_column(u'infopages_infopage', 'left_column_de', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_uk'
        db.alter_column(u'infopages_infopage', 'title_uk', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_it'
        db.alter_column(u'infopages_infopage', 'right_column_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_pl'
        db.alter_column(u'infopages_infopage', 'title_pl', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_uk'
        db.alter_column(u'infopages_infopage', 'right_column_uk', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_en'
        db.alter_column(u'infopages_infopage', 'title_en', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.left_column_pl'
        db.alter_column(u'infopages_infopage', 'left_column_pl', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_it'
        db.alter_column(u'infopages_infopage', 'left_column_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_es'
        db.alter_column(u'infopages_infopage', 'title_es', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.left_column_ru'
        db.alter_column(u'infopages_infopage', 'left_column_ru', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_de'
        db.alter_column(u'infopages_infopage', 'right_column_de', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_es'
        db.alter_column(u'infopages_infopage', 'left_column_es', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_en'
        db.alter_column(u'infopages_infopage', 'left_column_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_fr'
        db.alter_column(u'infopages_infopage', 'right_column_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_ru'
        db.alter_column(u'infopages_infopage', 'title_ru', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.title_it'
        db.alter_column(u'infopages_infopage', 'title_it', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

    def backwards(self, orm):

        # Changing field 'InfoPage.title_de'
        db.alter_column(u'infopages_infopage', 'title_de', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.left_column_uk'
        db.alter_column(u'infopages_infopage', 'left_column_uk', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_pl'
        db.alter_column(u'infopages_infopage', 'right_column_pl', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_lt'
        db.alter_column(u'infopages_infopage', 'right_column_lt', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_lt'
        db.alter_column(u'infopages_infopage', 'left_column_lt', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_ru'
        db.alter_column(u'infopages_infopage', 'right_column_ru', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_fr'
        db.alter_column(u'infopages_infopage', 'left_column_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_lt'
        db.alter_column(u'infopages_infopage', 'title_lt', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_es'
        db.alter_column(u'infopages_infopage', 'right_column_es', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_fr'
        db.alter_column(u'infopages_infopage', 'title_fr', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_en'
        db.alter_column(u'infopages_infopage', 'right_column_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_de'
        db.alter_column(u'infopages_infopage', 'left_column_de', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_uk'
        db.alter_column(u'infopages_infopage', 'title_uk', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_it'
        db.alter_column(u'infopages_infopage', 'right_column_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_pl'
        db.alter_column(u'infopages_infopage', 'title_pl', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.right_column_uk'
        db.alter_column(u'infopages_infopage', 'right_column_uk', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_en'
        db.alter_column(u'infopages_infopage', 'title_en', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.left_column_pl'
        db.alter_column(u'infopages_infopage', 'left_column_pl', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_it'
        db.alter_column(u'infopages_infopage', 'left_column_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_es'
        db.alter_column(u'infopages_infopage', 'title_es', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.left_column_ru'
        db.alter_column(u'infopages_infopage', 'left_column_ru', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_de'
        db.alter_column(u'infopages_infopage', 'right_column_de', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_es'
        db.alter_column(u'infopages_infopage', 'left_column_es', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.left_column_en'
        db.alter_column(u'infopages_infopage', 'left_column_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.right_column_fr'
        db.alter_column(u'infopages_infopage', 'right_column_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'InfoPage.title_ru'
        db.alter_column(u'infopages_infopage', 'title_ru', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

        # Changing field 'InfoPage.title_it'
        db.alter_column(u'infopages_infopage', 'title_it', self.gf('django.db.models.fields.CharField')(max_length=120, null=True))

    models = {
        u'infopages.infopage': {
            'Meta': {'ordering': "('main_page', 'slug')", 'object_name': 'InfoPage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_column': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'left_column_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_lt': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_pl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_ru': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'left_column_uk': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'main_page': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'right_column': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'right_column_de': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_lt': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_pl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_ru': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'right_column_uk': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'title_de': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_es': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_it': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_lt': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_pl': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'title_uk': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['infopages']