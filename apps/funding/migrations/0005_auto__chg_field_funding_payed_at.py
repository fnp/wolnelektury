# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Funding.payed_at'
        db.alter_column(u'funding_funding', 'payed_at', self.gf('django.db.models.fields.DateTimeField')(null=True))

    def backwards(self, orm):

        # Changing field 'Funding.payed_at'
        db.alter_column(u'funding_funding', 'payed_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 4, 16, 0, 0)))

    models = {
        'catalogue.book': {
            'Meta': {'ordering': "('sort_key',)", 'object_name': 'Book'},
            '_related_info': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'common_slug': ('django.db.models.fields.SlugField', [], {'max_length': '120'}),
            'cover': ('catalogue.fields.EbookField', [], {'max_length': '100', 'null': 'True', 'format_name': "'cover'", 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'epub_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'epub'", 'blank': 'True'}),
            'extra_info': ('jsonfield.fields.JSONField', [], {'default': "'{}'"}),
            'fb2_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'fb2'", 'blank': 'True'}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'html_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'html'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'pol'", 'max_length': '3', 'db_index': 'True'}),
            'mobi_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'mobi'", 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['catalogue.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pdf_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'pdf'", 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'txt_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'txt'", 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('catalogue.fields.EbookField', [], {'default': "''", 'max_length': '100', 'format_name': "'xml'", 'blank': 'True'})
        },
        u'funding.funding': {
            'Meta': {'ordering': "['-payed_at']", 'object_name': 'Funding'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['funding.Offer']"}),
            'payed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'perks': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['funding.Perk']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'funding.offer': {
            'Meta': {'ordering': "['-end']", 'object_name': 'Offer'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Book']", 'null': 'True', 'blank': 'True'}),
            'due': ('django.db.models.fields.DateField', [], {}),
            'end': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redakcja_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'target': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'funding.perk': {
            'Meta': {'ordering': "['-price']", 'object_name': 'Perk'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['funding.Offer']", 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'funding.spent': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Spent'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Book']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['funding']