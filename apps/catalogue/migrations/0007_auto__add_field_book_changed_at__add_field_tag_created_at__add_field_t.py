# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Book.changed_at'
        db.add_column('catalogue_book', 'changed_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2011, 2, 25, 15, 19, 36, 525463), db_index=True, blank=True), keep_default=False)

        # Adding index on 'Book', fields ['created_at']
        db.create_index('catalogue_book', ['created_at'])

        # Adding field 'Tag.created_at'
        db.add_column('catalogue_tag', 'created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2011, 2, 25, 15, 19, 42, 921525), db_index=True, blank=True), keep_default=False)

        # Adding field 'Tag.changed_at'
        db.add_column('catalogue_tag', 'changed_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2011, 2, 25, 15, 19, 45, 697471), db_index=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Removing index on 'Book', fields ['created_at']
        db.delete_index('catalogue_book', ['created_at'])

        # Deleting field 'Book.changed_at'
        db.delete_column('catalogue_book', 'changed_at')

        # Deleting field 'Tag.created_at'
        db.delete_column('catalogue_tag', 'created_at')

        # Deleting field 'Tag.changed_at'
        db.delete_column('catalogue_tag', 'changed_at')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'catalogue.book': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Book'},
            '_short_html': ('django.db.models.fields.TextField', [], {}),
            '_short_html_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_tag_counter': ('catalogue.fields.JSONField', [], {'null': 'True'}),
            '_theme_counter': ('catalogue.fields.JSONField', [], {'null': 'True'}),
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'epub_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'extra_info': ('catalogue.fields.JSONField', [], {}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medias': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['catalogue.BookMedia']", 'symmetrical': 'False', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'blank': 'True', 'null': 'True', 'to': "orm['catalogue.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'unique': 'True', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'txt_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'wiki_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'xml_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        },
        'catalogue.bookmedia': {
            'Meta': {'ordering': "('type', 'name')", 'object_name': 'BookMedia'},
            'extra_info': ('catalogue.fields.JSONField', [], {'default': "'{}'"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': "'100'"}),
            'uploaded_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'catalogue.filerecord': {
            'Meta': {'ordering': "('-time', '-slug', '-type')", 'object_name': 'FileRecord'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sha1': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'db_index': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
        'catalogue.fragment': {
            'Meta': {'ordering': "('book', 'anchor')", 'object_name': 'Fragment'},
            '_short_html': ('django.db.models.fields.TextField', [], {}),
            '_short_html_de': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_en': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_es': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_fr': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_lt': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_pl': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_ru': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            '_short_html_uk': ('django.db.models.fields.TextField', [], {'null': True, 'blank': True}),
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fragments'", 'to': "orm['catalogue.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_text': ('django.db.models.fields.TextField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'catalogue.tag': {
            'Meta': {'ordering': "('sort_key',)", 'unique_together': "(('slug', 'category'),)", 'object_name': 'Tag'},
            'book_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'changed_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'db_index': 'True'}),
            'sort_key': ('django.db.models.fields.CharField', [], {'max_length': '120', 'db_index': 'True'}),
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
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalogue']
