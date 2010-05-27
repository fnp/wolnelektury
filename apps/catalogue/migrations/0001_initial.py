# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Tag'
        db.create_table('catalogue_tag', (
            ('category', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('gazeta_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('main_page', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('sort_key', self.gf('django.db.models.fields.SlugField')(max_length=120, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wiki_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=120, db_index=True)),
            ('book_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal('catalogue', ['Tag'])

        # Adding model 'TagRelation'
        db.create_table('catalogue_tag_relation', (
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['catalogue.Tag'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('catalogue', ['TagRelation'])

        # Adding unique constraint on 'TagRelation', fields ['tag', 'content_type', 'object_id']
        db.create_unique('catalogue_tag_relation', ['tag_id', 'content_type_id', 'object_id'])

        # Adding model 'Book'
        db.create_table('catalogue_book', (
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['catalogue.Book'])),
            ('mp3_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('xml_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('wiki_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('txt_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('pdf_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('html_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('_short_html', self.gf('django.db.models.fields.TextField')()),
            ('parent_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ogg_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('odt_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=120, db_index=True)),
            ('gazeta_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('extra_info', self.gf('catalogue.fields.JSONField')()),
        ))
        db.send_create_signal('catalogue', ['Book'])

        # Adding model 'Fragment'
        db.create_table('catalogue_fragment', (
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('anchor', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('_short_html', self.gf('django.db.models.fields.TextField')()),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fragments', to=orm['catalogue.Book'])),
            ('short_text', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('catalogue', ['Fragment'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'Tag'
        db.delete_table('catalogue_tag')

        # Deleting model 'TagRelation'
        db.delete_table('catalogue_tag_relation')

        # Removing unique constraint on 'TagRelation', fields ['tag', 'content_type', 'object_id']
        db.delete_unique('catalogue_tag_relation', ['tag_id', 'content_type_id', 'object_id'])

        # Deleting model 'Book'
        db.delete_table('catalogue_book')

        # Deleting model 'Fragment'
        db.delete_table('catalogue_fragment')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'catalogue.book': {
            'Meta': {'object_name': 'Book'},
            '_short_html': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'extra_info': ('catalogue.fields.JSONField', [], {}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mp3_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'odt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'ogg_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['catalogue.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'txt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        'catalogue.fragment': {
            'Meta': {'object_name': 'Fragment'},
            '_short_html': ('django.db.models.fields.TextField', [], {}),
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fragments'", 'to': "orm['catalogue.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_text': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'catalogue.tag': {
            'Meta': {'object_name': 'Tag'},
            'book_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'sort_key': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'})
        },
        'catalogue.tagrelation': {
            'Meta': {'unique_together': "(('tag', 'content_type', 'object_id'),)", 'object_name': 'TagRelation', 'db_table': "'catalogue_tag_relation'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['catalogue.Tag']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }
    
    complete_apps = ['catalogue']
