# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Note'
        db.create_table('dictionary_note', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Book'])),
            ('anchor', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('sort_key', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
        ))
        db.send_create_signal('dictionary', ['Note'])


    def backwards(self, orm):
        
        # Deleting model 'Note'
        db.delete_table('dictionary_note')


    models = {
        'catalogue.book': {
            'Meta': {'ordering': "('sort_key',)", 'object_name': 'Book'},
            '_related_info': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'common_slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'db_index': 'True'}),
            'cover': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'epub_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'extra_info': ('jsonfield.fields.JSONField', [], {'default': "'{}'"}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'pol'", 'max_length': '3', 'db_index': 'True'}),
            'mobi_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['catalogue.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'txt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        'dictionary.note': {
            'Meta': {'ordering': "['sort_key']", 'object_name': 'Note'},
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Book']"}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'})
        }
    }

    complete_apps = ['dictionary']
