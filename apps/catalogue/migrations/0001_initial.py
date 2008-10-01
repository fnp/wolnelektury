from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from south.db import db


# Mock gettext
_ = lambda s: s


class Migration:
    
    def forwards(self):
        # Model 'Book'
        Book = db.mock_model(model_name='Book', db_table='catalogue_book', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.create_table('catalogue_book', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('title', models.CharField(_('title'), max_length=120)),
            ('slug', models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)),
            ('description', models.TextField(_('description'), blank=True)),
            ('created_at', models.DateTimeField(_('creation date'), auto_now=True)),
            ('_short_html', models.TextField(_('short HTML'), editable=False)),
            ('parent_number', models.IntegerField(_('parent number'), default=0)),
            ('xml_file', models.FileField(_('XML file'), blank=True)),
            ('html_file', models.FileField(_('HTML file'), blank=True)),
            ('pdf_file', models.FileField(_('PDF file'), blank=True)),
            ('odt_file', models.FileField(_('ODT file'), blank=True)),
            ('txt_file', models.FileField(_('TXT file'), blank=True)),
            ('parent', models.ForeignKey(Book, blank=True, null=True, related_name='children')),
        ))
        
        # Model 'Fragment'
        Fragment = db.mock_model(model_name='Fragment', db_table='catalogue_fragment', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.create_table('catalogue_fragment', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('text', models.TextField()),
            ('short_text', models.TextField(editable=False)),
            ('_short_html', models.TextField(editable=False)),
            ('anchor', models.CharField(max_length=120)),
            ('book', models.ForeignKey(Book, related_name='fragments')),
        ))
        
        # Model 'Tag'
        Tag = db.mock_model(model_name='Tag', db_table='catalogue_tag', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.create_table('catalogue_tag', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField(_('name'), max_length=50, db_index=True)),
            ('slug', models.SlugField(_('slug'), max_length=120, unique=True, db_index=True)),
            ('sort_key', models.SlugField(_('sort key'), max_length=120, db_index=True)),
            ('category', models.CharField(_('category'), max_length=50, blank=False, null=False, db_index=True)),
            ('description', models.TextField(_('description'), blank=True)),
            ('main_page', models.BooleanField(_('main page'), default=False, db_index=True, help_text=_('Show tag on main page'))),
            ('user', models.ForeignKey(User, blank=True, null=True)),
            ('book_count', models.IntegerField(_('book count'), default=0, blank=False, null=False)),
        ))
        
        # Model 'TagRelation'
        TagRelation = db.mock_model(model_name='TagRelation', db_table='catalogue_tag_relation', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.create_table('catalogue_tag_relation', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tag', models.ForeignKey(Tag, verbose_name=_('tag'), related_name='items')),
            ('content_type', models.ForeignKey(ContentType, verbose_name=_('content type'))),
            ('object_id', models.PositiveIntegerField(_('object id'), db_index=True)),
        ))
        
        db.send_create_signal('catalogue', ['Book','Fragment'])
    
    def backwards(self):
        db.delete_table('catalogue_tag_relation')
        db.delete_table('catalogue_tag')
        db.delete_table('catalogue_fragment')
        db.delete_table('catalogue_book')
        
