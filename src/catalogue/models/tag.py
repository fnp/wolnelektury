# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.core.cache import caches
from django.contrib.auth.models import User
from django.db import models
from django.db.models import permalink
from django.dispatch import Signal
from django.utils.translation import ugettext_lazy as _
from newtagging.models import TagBase
from ssify import flush_ssi_includes


# Those are hard-coded here so that makemessages sees them.
TAG_CATEGORIES = (
    ('author', _('author')),
    ('epoch', _('epoch')),
    ('kind', _('kind')),
    ('genre', _('genre')),
    ('theme', _('theme')),
    ('set', _('set')),
    ('thing', _('thing')),  # things shown on pictures
)


class Tag(TagBase):
    """A tag attachable to books and fragments (and possibly anything).

    Used to represent searchable metadata (authors, epochs, genres, kinds),
    fragment themes (motifs) and some book hierarchy related kludges."""
    name = models.CharField(_('name'), max_length=120, db_index=True)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True)
    category = models.CharField(
        _('category'), max_length=50, blank=False, null=False, db_index=True, choices=TAG_CATEGORIES)
    description = models.TextField(_('description'), blank=True)

    user = models.ForeignKey(User, blank=True, null=True)
    gazeta_link = models.CharField(blank=True, max_length=240)
    culturepl_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    created_at = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at = models.DateTimeField(_('creation date'), auto_now=True, db_index=True)

    after_change = Signal(providing_args=['instance', 'languages'])

    class UrlDeprecationWarning(DeprecationWarning):
        pass

    categories_rev = {
        'autor': 'author',
        'epoka': 'epoch',
        'rodzaj': 'kind',
        'gatunek': 'genre',
        'motyw': 'theme',
        'polka': 'set',
        'obiekt': 'thing',
    }
    categories_dict = dict((item[::-1] for item in categories_rev.iteritems()))

    class Meta:
        ordering = ('sort_key',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        unique_together = (("slug", "category"),)
        app_label = 'catalogue'

    def save(self, *args, **kwargs):
        flush_cache = flush_all_includes = False
        if self.pk and self.category != 'set':
            # Flush the whole views cache.
            # Seem a little harsh, but changed tag names, descriptions
            # and links come up at any number of places.
            flush_cache = True

            # Find in which languages we need to flush related includes.
            old_self = type(self).objects.get(pk=self.pk)
            # Category shouldn't normally be changed, but just in case.
            if self.category != old_self.category:
                flush_all_includes = True
            languages_changed = self.languages_changed(old_self)

        ret = super(Tag, self).save(*args, **kwargs)

        if flush_cache:
            caches[settings.CACHE_MIDDLEWARE_ALIAS].clear()
            if flush_all_includes:
                flush_ssi_includes()
            else:
                self.flush_includes()
            self.after_change.send(sender=type(self), instance=self, languages=languages_changed)

        return ret

    def languages_changed(self, old):
        all_langs = [lc for (lc, _ln) in settings.LANGUAGES]
        if (old.category, old.slug) != (self.category, self.slug):
            return all_langs
        languages = set()
        for lang in all_langs:
            name_field = 'name_%s' % lang
            if getattr(old, name_field) != getattr(self, name_field):
                languages.add(lang)
        return languages

    def flush_includes(self, languages=True):
        if not languages:
            return
        if languages is True:
            languages = [lc for (lc, _ln) in settings.LANGUAGES]
        flush_ssi_includes([
            template % (self.pk, lang)
            for template in [
                '/api/include/tag/%d.%s.json',
                '/api/include/tag/%d.%s.xml',
                ]
            for lang in languages
            ])
        flush_ssi_includes([
            '/katalog/%s.json' % lang for lang in languages])

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Tag(slug=%r)" % self.slug

    def get_initial(self):
        if self.category == 'author':
            return self.sort_key[0]
        elif self.name:
            return self.name[0]
        else:
            return ''

    @permalink
    def get_absolute_url(self):
        return 'tagged_object_list', [self.url_chunk]

    @permalink
    def get_absolute_gallery_url(self):
        return 'tagged_object_list_gallery', [self.url_chunk]

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

    @staticmethod
    def get_tag_list(tags):
        if isinstance(tags, basestring):
            if not tags:
                return []
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
                        real_tags.append(Tag.objects.get(slug=name))
                        deprecated = True
                    except Tag.MultipleObjectsReturned:
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
            except KeyError:
                try:
                    tag_names = [getattr(info, category)]
                except KeyError:
                    # For instance, Pictures do not have 'genre' field.
                    continue
            for tag_name in tag_names:
                lang = getattr(tag_name, 'lang', settings.LANGUAGE_CODE)
                tag_sort_key = tag_name
                if category == 'author':
                    tag_sort_key = ' '.join((tag_name.last_name,) + tag_name.first_names)
                    tag_name = tag_name.readable()
                if lang == settings.LANGUAGE_CODE:
                    # Allow creating new tag, if it's in default language.
                    tag, created = Tag.objects.get_or_create(slug=slughifi(tag_name), category=category)
                    if created:
                        tag_name = unicode(tag_name)
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


# Pickle complains about not having this.
TagRelation = Tag.intermediary_table_model
