# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Deleted'
        db.create_table('api_deleted', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length='50')),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('api', ['Deleted'])

        # Adding unique constraint on 'Deleted', fields ['type', 'object_id']
        db.create_unique('api_deleted', ['type', 'object_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Deleted', fields ['type', 'object_id']
        db.delete_unique('api_deleted', ['type', 'object_id'])

        # Deleting model 'Deleted'
        db.delete_table('api_deleted')


    models = {
        'api.deleted': {
            'Meta': {'unique_together': "(('type', 'object_id'),)", 'object_name': 'Deleted'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'50'"})
        }
    }

    complete_apps = ['api']
