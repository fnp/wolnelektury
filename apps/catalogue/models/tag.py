# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext, ugettext_lazy as _
from newtagging.models import TagBase


# Those are hard-coded here so that makemessages sees them.
TAG_CATEGORIES = (
    ('author', _('author')),
    ('epoch', _('epoch')),
    ('kind', _('kind')),
    ('genre', _('genre')),
    ('theme', _('theme')),
    ('set', _('set')),
    ('book', _('book')),
)


class Tag(TagBase):
    """A tag attachable to books and fragments (and possibly anything).
    
    Used to represent searchable metadata (authors, epochs, genres, kinds),
    fragment themes (motifs) and some book hierarchy related kludges."""
    name = models.CharField(_('name'), max_length=50, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True)
    category = models.CharField(_('category'), max_length=50, blank=False, null=False,
        db_index=True, choices=TAG_CATEGORIES)
    description = models.TextField(_('description'), blank=True)

    user = models.ForeignKey(User, blank=True, null=True)
    book_count = models.IntegerField(_('book count'), blank=True, null=True)
    gazeta_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    created_at    = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at    = models.DateTimeField(_('creation date'), auto_now=True, db_index=True)

    class UrlDeprecationWarning(DeprecationWarning):
        pass

    categories_rev = {
        'autor': 'author',
        'epoka': 'epoch',
        'rodzaj': 'kind',
        'gatunek': 'genre',
        'motyw': 'theme',
        'polka': 'set',
    }
    categories_dict = dict((item[::-1] for item in categories_rev.iteritems()))

    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        unique_together = (("slug", "category"),)
        app_label = 'catalogue'

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Tag(slug=%r)" % self.slug

    @permalink
    def get_absolute_url(self):
        return ('catalogue.views.tagged_object_list', [self.url_chunk])

    def clean(self):
        if self.category == 'book' and (self.gazeta_link or self.wiki_link):
            raise ValidationError(ugettext(
                u"Book tags can't have attached links. Set them directly on the book instead of it's tag."))

    @classmethod
    @permalink
    def create_url(cls, category, slug):
        return ('catalogue.views.tagged_object_list', [
                '/'.join((cls.categories_dict[category], slug))
            ])

    def has_description(self):
        return len(self.description) > 0
    has_description.short_description = _('description')
    has_description.boolean = True

    def get_count(self):
        """Returns global book count for book tags, fragment count for themes."""
        from catalogue.models import Book, Fragment

        if self.category == 'book':
            # never used
            objects = Book.objects.none()
        elif self.category == 'theme':
            objects = Fragment.tagged.with_all((self,))
        else:
            objects = Book.tagged.with_all((self,)).order_by()
            if self.category != 'set':
                # eliminate descendants
                l_tags = Tag.objects.filter(slug__in=[book.book_tag_slug() for book in objects.iterator()])
                descendants_keys = [book.pk for book in Book.tagged.with_any(l_tags).iterator()]
                if descendants_keys:
                    objects = objects.exclude(pk__in=descendants_keys)
        return objects.count()

    @staticmethod
    def get_tag_list(tags):
        if isinstance(tags, basestring):
            real_tags = []
            ambiguous_slugs = []
            category = None
            deprecated = False
            tags_splitted = tags.split('/')
            for name in tags_splitted:
                if category:
                    real_tags.append(Tag.objects.get(slug=name, category=category))
                    category = None
                elif name in Tag.categories_rev:
                    category = Tag.categories_rev[name]
                else:
                    try:
                        real_tags.append(Tag.objects.exclude(category='book').get(slug=name))
                        deprecated = True 
                    except Tag.MultipleObjectsReturned, e:
                        ambiguous_slugs.append(name)

            if category:
                # something strange left off
                raise Tag.DoesNotExist()
            if ambiguous_slugs:
                # some tags should be qualified
                e = Tag.MultipleObjectsReturned()
                e.tags = real_tags
                e.ambiguous_slugs = ambiguous_slugs
                raise e
            if deprecated:
                e = Tag.UrlDeprecationWarning()
                e.tags = real_tags
                raise e
            return real_tags
        else:
            return TagBase.get_tag_list(tags)

    @property
    def url_chunk(self):
        return '/'.join((Tag.categories_dict[self.category], self.slug))

    @staticmethod
    def tags_from_info(info):
        from fnpdjango.utils.text.slughifi import slughifi
        from sortify import sortify
        meta_tags = []
        categories = (('kinds', 'kind'), ('genres', 'genre'), ('authors', 'author'), ('epochs', 'epoch'))
        for field_name, category in categories:
            try:
                tag_names = getattr(info, field_name)
            except:
                try:
                    tag_names = [getattr(info, category)]
                except:
                    # For instance, Pictures do not have 'genre' field.
                    continue
            for tag_name in tag_names:
                lang = getattr(tag_name, 'lang', settings.LANGUAGE_CODE)
                tag_sort_key = tag_name
                if category == 'author':
                    tag_sort_key = tag_name.last_name
                    tag_name = tag_name.readable()
                if lang == settings.LANGUAGE_CODE:
                    # Allow creating new tag, if it's in default language.
                    tag, created = Tag.objects.get_or_create(slug=slughifi(tag_name), category=category)
                    if created:
                        tag.name = tag_name
                        setattr(tag, "name_%s" % lang, tag_name)
                        tag.sort_key = sortify(tag_sort_key.lower())
                        tag.save()
                    meta_tags.append(tag)
                else:
                    # Ignore unknown tags in non-default languages.
                    try:
                        tag = Tag.objects.get(category=category, **{"name_%s" % lang: tag_name})
                    except Tag.DoesNotExist:
                        pass
                    else:
                        meta_tags.append(tag)
        return meta_tags
