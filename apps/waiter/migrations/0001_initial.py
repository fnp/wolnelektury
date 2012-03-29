# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WaitedFile'
        db.create_table('waiter_waitedfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('task', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('waiter', ['WaitedFile'])


    def backwards(self, orm):
        
        # Deleting model 'WaitedFile'
        db.delete_table('waiter_waitedfile')


    models = {
        'waiter.waitedfile': {
            'Meta': {'object_name': 'WaitedFile'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'task': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['waiter']
