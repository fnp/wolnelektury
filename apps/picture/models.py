# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models, transaction
import catalogue.models
from django.db.models import permalink
from sorl.thumbnail import ImageField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import SortedDict
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.cache import caches
from catalogue.utils import split_tags
from fnpdjango.utils.text.slughifi import slughifi
from picture import tasks
from StringIO import StringIO
import jsonfield
import itertools
import logging

from PIL import Image

from django.utils.translation import get_language, ugettext_lazy as _
from newtagging import managers
from os import path


permanent_cache = caches['permanent']

picture_storage = FileSystemStorage(location=path.join(
        settings.MEDIA_ROOT, 'pictures'),
        base_url=settings.MEDIA_URL + "pictures/")


class PictureArea(models.Model):
    picture = models.ForeignKey('picture.Picture', related_name='areas')
    area = jsonfield.JSONField(_('area'), default={}, editable=False)
    kind = models.CharField(_('kind'), max_length=10, blank=False,
                           null=False, db_index=True,
                           choices=(('thing', _('thing')),
                                    ('theme', _('theme'))))

    objects     = models.Manager()
    tagged      = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags        = managers.TagDescriptor(catalogue.models.Tag)
    tag_relations = GenericRelation(catalogue.models.Tag.intermediary_table_model)

    @classmethod
    def rectangle(cls, picture, kind, coords):
        pa = PictureArea()
        pa.picture = picture
        pa.kind = kind
        pa.area = coords
        return pa

    def reset_short_html(self):
        if self.id is None:
            return

        cache_key = "PictureArea.short_html/%d/%s"
        for lang, langname in settings.LANGUAGES:
            permanent_cache.delete(cache_key % (self.id, lang))


    def short_html(self):
        if self.id:
            cache_key = "PictureArea.short_html/%d/%s" % (self.id, get_language())
            short_html = permanent_cache.get(cache_key)
        else:
            short_html = None

        if short_html is not None:
            return mark_safe(short_html)
        else:
            theme = self.tags.filter(category='theme')
            theme = theme and theme[0] or None
            thing = self.tags.filter(category='thing')
            thing = thing and thing[0] or None
            area = self
            short_html = unicode(render_to_string(
                    'picture/picturearea_short.html', locals()))
            if self.id:
                permanent_cache.set(cache_key, short_html)
            return mark_safe(short_html)


class Picture(models.Model):
    """
    Picture resource.

    """
    title       = models.CharField(_('title'), max_length=120)
    slug        = models.SlugField(_('slug'), max_length=120, db_index=True, unique=True)
    sort_key    = models.CharField(_('sort key'), max_length=120, db_index=True, editable=False)
    sort_key_author = models.CharField(_('sort key by author'), max_length=120, db_index=True, editable=False, default=u'')
    created_at  = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at  = models.DateTimeField(_('creation date'), auto_now=True, db_index=True)
    xml_file    = models.FileField('xml_file', upload_to="xml", storage=picture_storage)
    image_file  = ImageField(_('image_file'), upload_to="images", storage=picture_storage)
    html_file   = models.FileField('html_file', upload_to="html", storage=picture_storage)
    areas_json       = jsonfield.JSONField(_('picture areas JSON'), default={}, editable=False)
    extra_info    = jsonfield.JSONField(_('extra information'), default={})
    culturepl_link   = models.CharField(blank=True, max_length=240)
    wiki_link     = models.CharField(blank=True, max_length=240)

    _related_info = jsonfield.JSONField(blank=True, null=True, editable=False)

    width       = models.IntegerField(null=True)
    height      = models.IntegerField(null=True)

    objects     = models.Manager()
    tagged      = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags        = managers.TagDescriptor(catalogue.models.Tag)
    tag_relations = GenericRelation(catalogue.models.Tag.intermediary_table_model)

    class AlreadyExists(Exception):
        pass

    class Meta:
        ordering = ('sort_key',)

        verbose_name = _('picture')
        verbose_name_plural = _('pictures')

    def save(self, force_insert=False, force_update=False, reset_short_html=True, **kwargs):
        from sortify import sortify

        self.sort_key = sortify(self.title)

        ret = super(Picture, self).save(force_insert, force_update)

        if reset_short_html:
            self.reset_short_html()

        return ret

    def __unicode__(self):
        return self.title

    @permalink
    def get_absolute_url(self):
        return ('picture.views.picture_detail', [self.slug])

    @classmethod
    def from_xml_file(cls, xml_file, image_file=None, image_store=None, overwrite=False):
        """
        Import xml and it's accompanying image file.
        If image file is missing, it will be fetched by librarian.picture.ImageStore
        which looks for an image file in the same directory the xml is, with extension matching
        its mime type.
        """
        from sortify import sortify
        from django.core.files import File
        from librarian.picture import WLPicture, ImageStore
        close_xml_file = False
        close_image_file = False


        if image_file is not None and not isinstance(image_file, File):
            image_file = File(open(image_file))
            close_image_file = True

        if not isinstance(xml_file, File):
            xml_file = File(open(xml_file))
            close_xml_file = True

        try:
            # use librarian to parse meta-data
            if image_store is None:
                image_store = ImageStore(picture_storage.path('images'))
            picture_xml = WLPicture.from_file(xml_file, image_store=image_store)

            picture, created = Picture.objects.get_or_create(slug=picture_xml.slug)
            if not created and not overwrite:
                raise Picture.AlreadyExists('Picture %s already exists' % picture_xml.slug)

            picture.areas.all().delete()
            picture.title = unicode(picture_xml.picture_info.title)
            picture.extra_info = picture_xml.picture_info.to_dict()

            picture_tags = set(catalogue.models.Tag.tags_from_info(picture_xml.picture_info))
            motif_tags = set()
            thing_tags = set()

            area_data = {'themes':{}, 'things':{}}

            for part in picture_xml.partiter():
                if picture_xml.frame:
                    c = picture_xml.frame[0]
                    part['coords'] = [[p[0] - c[0], p[1] - c[1]] for p in part['coords']]
                if part.get('object', None) is not None:
                    objname = part['object']
                    tag, created = catalogue.models.Tag.objects.get_or_create(slug=slughifi(objname), category='thing')
                    if created:
                        tag.name = objname
                        tag.sort_key = sortify(tag.name)
                        tag.save()
                    #thing_tags.add(tag)
                    area_data['things'][tag.slug] = {
                        'object': part['object'],
                        'coords': part['coords'],
                        }
                    area = PictureArea.rectangle(picture, 'thing', part['coords'])
                    area.save()
                    _tags = set()
                    _tags.add(tag)
                    area.tags = _tags
                else:
                    _tags = set()
                    for motif in part['themes']:
                        tag, created = catalogue.models.Tag.objects.get_or_create(slug=slughifi(motif), category='theme')
                        if created:
                            tag.name = motif
                            tag.sort_key = sortify(tag.name)
                            tag.save()
                        #motif_tags.add(tag)
                        _tags.add(tag)
                        area_data['themes'][tag.slug] = {
                            'theme': motif,
                            'coords': part['coords']
                            }

                    logging.debug("coords for theme: %s" % part['coords'])
                    area = PictureArea.rectangle(picture, 'theme', part['coords'])
                    area.save()
                    area.tags = _tags.union(picture_tags)

            picture.tags = picture_tags.union(motif_tags).union(thing_tags)
            picture.areas_json = area_data

            if image_file is not None:
                img = image_file
            else:
                img = picture_xml.image_file()

            modified = cls.crop_to_frame(picture_xml, img)
            modified = cls.add_source_note(picture_xml, modified)

            picture.width, picture.height = modified.size

            modified_file = StringIO()
            modified.save(modified_file, format='png', quality=95)
            # FIXME: hardcoded extension - detect from DC format or orginal filename
            picture.image_file.save(path.basename(picture_xml.image_path), File(modified_file))

            picture.xml_file.save("%s.xml" % picture.slug, File(xml_file))
            picture.save()
            tasks.generate_picture_html(picture.id)

        except Exception, ex:
            logging.exception("Exception during import, rolling back")
            transaction.rollback()
            raise ex

        finally:
            if close_xml_file:
                xml_file.close()
            if close_image_file:
                image_file.close()

        transaction.commit()

        return picture

    @classmethod
    def crop_to_frame(cls, wlpic, image_file):
        img = Image.open(image_file)
        if wlpic.frame is None:
            return img
        img = img.crop(itertools.chain(*wlpic.frame))
        return img

    @staticmethod
    def add_source_note(wlpic, img):
        from PIL import ImageDraw, ImageFont
        from librarian import get_resource

        annotated = Image.new(img.mode,
                (img.size[0], img.size[1] + 40),
                (255, 255, 255)
            )
        annotated.paste(img, (0, 0))
        annotation = Image.new(img.mode, (3000, 120), (255, 255, 255))
        ImageDraw.Draw(annotation).text(
            (30, 15),
            wlpic.picture_info.source_name,
            (0, 0, 0),
            font=ImageFont.truetype(get_resource("fonts/DejaVuSerif.ttf"), 75)
        )
        annotated.paste(annotation.resize((1000, 40), Image.ANTIALIAS), (0, img.size[1]))
        return annotated

    @classmethod
    def picture_list(cls, filter=None):
        """Generates a hierarchical listing of all pictures
        Pictures are optionally filtered with a test function.
        """

        pics = cls.objects.all().order_by('sort_key')\
            .only('title', 'slug', 'image_file')

        if filter:
            pics = pics.filter(filter).distinct()

        pics_by_author = SortedDict()
        orphans = []
        for tag in catalogue.models.Tag.objects.filter(category='author'):
            pics_by_author[tag] = []

        for pic in pics.iterator():
            authors = list(pic.tags.filter(category='author'))
            if authors:
                for author in authors:
                    pics_by_author[author].append(pic)
            else:
                orphans.append(pic)

        return pics_by_author, orphans

    @property
    def info(self):
        if not hasattr(self, '_info'):
            from librarian import dcparser
            from librarian import picture
            info = dcparser.parse(self.xml_file.path, picture.PictureInfo)
            self._info = info
        return self._info

    def reset_short_html(self):
        if self.id is None:
            return

        type(self).objects.filter(pk=self.pk).update(_related_info=None)
        for area in self.areas.all().iterator():
            area.reset_short_html()

        try:
            author = self.tags.filter(category='author')[0].sort_key
        except IndexError:
            author = u''
        type(self).objects.filter(pk=self.pk).update(sort_key_author=author)

        cache_key = "Picture.short_html/%d/%s"
        for lang, langname in settings.LANGUAGES:
            permanent_cache.delete(cache_key % (self.id, lang))

    def short_html(self):
        if self.id:
            cache_key = "Picture.short_html/%d/%s" % (self.id, get_language())
            short_html = get_cache('permanent').get(cache_key)
        else:
            short_html = None

        if short_html is not None:
            return mark_safe(short_html)
        else:
            tags = self.tags.filter(category__in=('author', 'kind', 'epoch', 'genre'))
            tags = split_tags(tags)

            short_html = unicode(render_to_string(
                    'picture/picture_short.html',
                    {'picture': self, 'tags': tags}))

            if self.id:
                get_cache('permanent').set(cache_key, short_html)
            return mark_safe(short_html)

    def pretty_title(self, html_links=False):
        picture = self
        # TODO Add translations (related_tag_info)
        names = [(tag.name,
                  catalogue.models.Tag.create_url('author', tag.slug))
                 for tag in self.tags.filter(category='author')]
        names.append((self.title, self.get_absolute_url()))

        if html_links:
            names = ['<a href="%s">%s</a>' % (tag[1], tag[0]) for tag in names]
        else:
            names = [tag[0] for tag in names]
        return ', '.join(names)

    def related_info(self):
        """Keeps info about related objects (tags) in cache field."""
        if self._related_info is not None:
            return self._related_info
        else:
            rel = {'tags': {}}

            tags = self.tags.filter(category__in=(
                    'author', 'kind', 'genre', 'epoch'))
            tags = split_tags(tags)
            for category in tags:
                cat = []
                for tag in tags[category]:
                    tag_info = {'slug': tag.slug, 'name': tag.name}
                    for lc, ln in settings.LANGUAGES:
                        tag_name = getattr(tag, "name_%s" % lc)
                        if tag_name:
                            tag_info["name_%s" % lc] = tag_name
                    cat.append(tag_info)
                rel['tags'][category] = cat


            if self.pk:
                type(self).objects.filter(pk=self.pk).update(_related_info=rel)
            return rel

    # copied from book.py, figure out
    def related_themes(self):
        # self.theme_counter hides a computation, so a line below actually makes sense
        theme_counter = self.theme_counter
        picture_themes = list(catalogue.models.Tag.objects.filter(pk__in=theme_counter.keys()))
        for tag in picture_themes:
            tag.count = theme_counter[tag.pk]
        return picture_themes

    def reset_tag_counter(self):
        if self.id is None:
            return

        cache_key = "Picture.tag_counter/%d" % self.id
        permanent_cache.delete(cache_key)
        if self.parent:
            self.parent.reset_tag_counter()

    @property
    def tag_counter(self):
        if self.id:
            cache_key = "Picture.tag_counter/%d" % self.id
            tags = permanent_cache.get(cache_key)
        else:
            tags = None

        if tags is None:
            tags = {}
            # do we need to do this? there are no children here.
            for tag in self.tags.exclude(category__in=('book', 'theme', 'thing', 'set')).order_by().iterator():
                tags[tag.pk] = 1

            if self.id:
                permanent_cache.set(cache_key, tags)
        return tags

    def reset_theme_counter(self):
        if self.id is None:
            return

        cache_key = "Picture.theme_counter/%d" % self.id
        permanent_cache.delete(cache_key)

    @property
    def theme_counter(self):
        if self.id:
            cache_key = "Picture.theme_counter/%d" % self.id
            tags = permanent_cache.get(cache_key)
        else:
            tags = None

        if tags is None:
            tags = {}
            for area in PictureArea.objects.filter(picture=self).order_by().iterator():
                for tag in area.tags.filter(category__in=('theme', 'thing')).order_by().iterator():
                    tags[tag.pk] = tags.get(tag.pk, 0) + 1

            if self.id:
                permanent_cache.set(cache_key, tags)
        return tags
