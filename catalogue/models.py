# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from newtagging.models import TagBase
from newtagging import managers


TAG_CATEGORIES = (
    ('author', _('author')),
    ('epoch', _('epoch')),
    ('kind', _('kind')),
    ('genre', _('genre')),
    ('theme', _('theme')),
    ('set', _('set')),
)


class TagSubcategoryManager(models.Manager):
    def __init__(self, subcategory):
        super(TagSubcategoryManager, self).__init__()
        self.subcategory = subcategory
        
    def get_query_set(self):
        return super(TagSubcategoryManager, self).get_query_set().filter(category=self.subcategory)


class Tag(TagBase):
    name = models.CharField(_('name'), max_length=50, unique=True, db_index=True)
    slug = models.SlugField(_('slug'), unique=True, db_index=True)
    sort_key = models.SlugField(_('sort key'), db_index=True)
    category = models.CharField(_('category'), max_length=50, blank=False, null=False, 
        db_index=True, choices=TAG_CATEGORIES)
    description = models.TextField(blank=True)
    
    user = models.ForeignKey(User, blank=True, null=True)
    
    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('Has description')
    has_description.boolean = True

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.tagged_book_list', [self.slug])
    
    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
    
    def __unicode__(self):
        return self.name

    @staticmethod
    def get_tag_list(tags):
        if isinstance(tags, basestring):
            tag_slugs = tags.split('/')
            return [Tag.objects.get(slug=slug) for slug in tag_slugs]
        else:
            return TagBase.get_tag_list(tags)


class Book(models.Model):
    title = models.CharField(_('title'), max_length=120)
    slug = models.SlugField(_('slug'), unique=True, db_index=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(_('creation date'), auto_now=True)
    
    # Formats
    pdf_file = models.FileField(_('PDF file'), upload_to='books/pdf', blank=True)
    odt_file = models.FileField(_('ODT file'), upload_to='books/odt', blank=True)
    html_file = models.FileField(_('HTML file'), upload_to='books/html', blank=True)
    
    objects = managers.ModelTaggedItemManager(Tag)
    tags = managers.TagDescriptor(Tag)
    
    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('Has description')
    has_description.boolean = True
    
    def has_pdf_file(self):
        return bool(self.pdf_file)
    has_pdf_file.short_description = 'PDF'
    has_pdf_file.boolean = True
    
    def has_odt_file(self):
        return bool(self.odt_file)
    has_odt_file.short_description = 'ODT'
    has_odt_file.boolean = True
    
    def has_html_file(self):
        return bool(self.html_file)
    has_html_file.short_description = 'HTML'
    has_html_file.boolean = True
    
    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.book_detail', [self.slug])
        
    class Meta:
        ordering = ('title',)
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __unicode__(self):
        return self.title


# class Fragment(models.Model):
#     id = models.IntegerField(primary_key=True)
#     text = models.TextField(blank=True)
#     start_paragraph = models.IntegerField(null=True, blank=True)
#     book_id = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'fragment'


# class Inflections(models.Model):
#     word = models.CharField(max_length=120, primary_key=True)
#     cases = models.TextField() # This field type is a guess.
#     class Meta:
#         db_table = u'inflections'


# class Paragraph(models.Model):
#     id = models.IntegerField(primary_key=True)
#     number = models.IntegerField(null=True, blank=True)
#     text = models.TextField(blank=True)
#     book_id = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'paragraph'

