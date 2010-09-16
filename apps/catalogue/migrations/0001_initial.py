# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Tag'
        db.create_table('catalogue_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, db_index=True)),
            ('sort_key', self.gf('django.db.models.fields.SlugField')(max_length=120, db_index=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('main_page', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('book_count', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('death', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('gazeta_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('wiki_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
        ))
        db.send_create_signal('catalogue', ['Tag'])

        # Adding unique constraint on 'Tag', fields ['slug', 'category']
        db.create_unique('catalogue_tag', ['slug', 'category'])

        # Adding model 'TagRelation'
        db.create_table('catalogue_tag_relation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['catalogue.Tag'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('catalogue', ['TagRelation'])

        # Adding unique constraint on 'TagRelation', fields ['tag', 'content_type', 'object_id']
        db.create_unique('catalogue_tag_relation', ['tag_id', 'content_type_id', 'object_id'])

        # Adding model 'Book'
        db.create_table('catalogue_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=120, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('_short_html', self.gf('django.db.models.fields.TextField')()),
            ('_short_html_de', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_es', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_lt', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_pl', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_ru', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_uk', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('parent_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('extra_info', self.gf('catalogue.fields.JSONField')()),
            ('gazeta_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('wiki_link', self.gf('django.db.models.fields.CharField')(max_length=240, blank=True)),
            ('xml_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('html_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('pdf_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('epub_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('odt_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('txt_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('mp3_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('ogg_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['catalogue.Book'])),
            ('_tag_counter', self.gf('catalogue.fields.JSONField')(null=True)),
            ('_theme_counter', self.gf('catalogue.fields.JSONField')(null=True)),
        ))
        db.send_create_signal('catalogue', ['Book'])

        # Adding model 'Fragment'
        db.create_table('catalogue_fragment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('short_text', self.gf('django.db.models.fields.TextField')()),
            ('_short_html', self.gf('django.db.models.fields.TextField')()),
            ('_short_html_de', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_es', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_lt', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_pl', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_ru', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_short_html_uk', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('anchor', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fragments', to=orm['catalogue.Book'])),
        ))
        db.send_create_signal('catalogue', ['Fragment'])

        # Adding model 'BookStub'
        db.create_table('catalogue_bookstub', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('pd', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=120, db_index=True)),
            ('translator', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('translator_death', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('catalogue', ['BookStub'])

        # Adding model 'FileRecord'
        db.create_table('catalogue_filerecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=120, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('sha1', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('catalogue', ['FileRecord'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'TagRelation', fields ['tag', 'content_type', 'object_id']
        db.delete_unique('catalogue_tag_relation', ['tag_id', 'content_type_id', 'object_id'])

        # Removing unique constraint on 'Tag', fields ['slug', 'category']
        db.delete_unique('catalogue_tag', ['slug', 'category'])

        # Deleting model 'Tag'
        db.delete_table('catalogue_tag')

        # Deleting model 'TagRelation'
        db.delete_table('catalogue_tag_relation')

        # Deleting model 'Book'
        db.delete_table('catalogue_book')

        # Deleting model 'Fragment'
        db.delete_table('catalogue_fragment')

        # Deleting model 'BookStub'
        db.delete_table('catalogue_bookstub')

        # Deleting model 'FileRecord'
        db.delete_table('catalogue_filerecord')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'epub_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
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
        'catalogue.bookstub': {
            'Meta': {'ordering': "('title',)", 'object_name': 'BookStub'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pd': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '120', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'translator': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'translator_death': ('django.db.models.fields.TextField', [], {'blank': 'True'})
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
            'book_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'death': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gazeta_link': ('django.db.models.fields.CharField', [], {'max_length': '240', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'main_page': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '120', 'db_index': 'True'}),
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
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalogue']
