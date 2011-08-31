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
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('api', ['Deleted'])

        # Adding unique constraint on 'Deleted', fields ['content_type', 'object_id']
        db.create_unique('api_deleted', ['content_type_id', 'object_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Deleted', fields ['content_type', 'object_id']
        db.delete_unique('api_deleted', ['content_type_id', 'object_id'])

        # Deleting model 'Deleted'
        db.delete_table('api_deleted')


    models = {
        'api.deleted': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'Deleted'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']
