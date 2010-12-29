# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Author'
        db.create_table('pdcounter_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, unique=True, db_index=True)),
            ('sort_key', self.gf('django.db.models.fields.CharField')(max_length=120, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('death', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('gazeta_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('wiki_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
        ))
        db.send_create_signal('pdcounter', ['Author'])

        # Adding model 'BookStub'
        db.create_table('pdcounter_bookstub', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('pd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, unique=True, db_index=True)),
            ('translator', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('pdcounter', ['BookStub'])


    def backwards(self, orm):
        
        # Deleting model 'Author'
        db.delete_table('pdcounter_author')

        # Deleting model 'BookStub'
        db.delete_table('pdcounter_bookstub')


    models = {
        'pdcounter.author': {
            'Meta': {'ordering': "('sort_key',)", 'object_name': 'Author'},
            'death': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'unique': 'True', 'db_index': 'True'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'})
        },
        'pdcounter.bookstub': {
            'Meta': {'ordering': "('title',)", 'object_name': 'BookStub'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'unique': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'translator': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['pdcounter']
