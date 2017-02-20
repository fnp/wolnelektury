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
from fnpdjango.utils.text.slughifi import slughifi
from ssify import flush_ssi_includes

from catalogue.models.tag import prefetched_relations
from picture import tasks
from StringIO import StringIO
import jsonfield
import itertools
import logging
import re

from PIL import Image

from django.utils.translation import ugettext_lazy as _
from newtagging import managers
from os import path


picture_storage = FileSystemStorage(location=path.join(
        settings.MEDIA_ROOT, 'pictures'),
        base_url=settings.MEDIA_URL + "pictures/")


class PictureArea(models.Model):
    picture = models.ForeignKey('picture.Picture', related_name='areas')
    area = jsonfield.JSONField(_('area'), default={}, editable=False)
    kind = models.CharField(
        _('kind'), max_length=10, blank=False, null=False, db_index=True,
        choices=(('thing', _('thing')), ('theme', _('theme'))))

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags = managers.TagDescriptor(catalogue.models.Tag)
    tag_relations = GenericRelation(catalogue.models.Tag.intermediary_table_model)

    short_html_url_name = 'picture_area_short'

    @classmethod
    def rectangle(cls, picture, kind, coords):
        pa = PictureArea()
        pa.picture = picture
        pa.kind = kind
        pa.area = coords
        return pa

    def flush_includes(self, languages=True):
        if not languages:
            return
        if languages is True:
            languages = [lc for (lc, _ln) in settings.LANGUAGES]
        flush_ssi_includes([
            template % (self.pk, lang)
            for template in [
                '/katalog/pa/%d/short.%s.html',
                ]
            for lang in languages
            ])


class Picture(models.Model):
    """
    Picture resource.

    """
    title = models.CharField(_('title'), max_length=32767)
    slug = models.SlugField(_('slug'), max_length=120, db_index=True, unique=True)
    sort_key = models.CharField(_('sort key'), max_length=120, db_index=True, editable=False)
    sort_key_author = models.CharField(
        _('sort key by author'), max_length=120, db_index=True, editable=False, default=u'')
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at = models.DateTimeField(_('creation date'), auto_now=True, db_index=True)
    xml_file = models.FileField(_('xml file'), upload_to="xml", storage=picture_storage)
    image_file = ImageField(_('image file'), upload_to="images", storage=picture_storage)
    html_file = models.FileField(_('html file'), upload_to="html", storage=picture_storage)
    areas_json = jsonfield.JSONField(_('picture areas JSON'), default={}, editable=False)
    extra_info = jsonfield.JSONField(_('extra information'), default={})
    culturepl_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags = managers.TagDescriptor(catalogue.models.Tag)
    tag_relations = GenericRelation(catalogue.models.Tag.intermediary_table_model)

    short_html_url_name = 'picture_short'

    class AlreadyExists(Exception):
        pass

    class Meta:
        ordering = ('sort_key_author', 'sort_key')

        verbose_name = _('picture')
        verbose_name_plural = _('pictures')

    def save(self, force_insert=False, force_update=False, **kwargs):
        from sortify import sortify

        self.sort_key = sortify(self.title)[:120]

        try:
            author = self.authors().first().sort_key
        except AttributeError:
            author = u''
        self.sort_key_author = author

        ret = super(Picture, self).save(force_insert, force_update)

        return ret

    def __unicode__(self):
        return self.title

    def authors(self):
        return self.tags.filter(category='author')

    def tag_unicode(self, category):
        relations = prefetched_relations(self, category)
        if relations:
            return ', '.join(rel.tag.name for rel in relations)
        else:
            return ', '.join(self.tags.filter(category=category).values_list('name', flat=True))

    def author_unicode(self):
        return self.tag_unicode('author')

    @permalink
    def get_absolute_url(self):
        return 'picture.views.picture_detail', [self.slug]

    def get_initial(self):
        try:
            return re.search(r'\w', self.title, re.U).group(0)
        except AttributeError:
            return ''

    def get_next(self):
        try:
            return type(self).objects.filter(sort_key__gt=self.sort_key)[0]
        except IndexError:
            return None

    def get_previous(self):
        try:
            return type(self).objects.filter(sort_key__lt=self.sort_key).order_by('-sort_key')[0]
        except IndexError:
            return None

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

        with transaction.atomic():
            # use librarian to parse meta-data
            if image_store is None:
                image_store = ImageStore(picture_storage.path('images'))
            picture_xml = WLPicture.from_file(xml_file, image_store=image_store)

            picture, created = Picture.objects.get_or_create(slug=picture_xml.slug[:120])
            if not created and not overwrite:
                raise Picture.AlreadyExists('Picture %s already exists' % picture_xml.slug)

            picture.areas.all().delete()
            picture.title = unicode(picture_xml.picture_info.title)
            picture.extra_info = picture_xml.picture_info.to_dict()

            picture_tags = set(catalogue.models.Tag.tags_from_info(picture_xml.picture_info))

            area_data = {'themes': {}, 'things': {}}

            # Treat all names in picture XML as in default language.
            lang = settings.LANGUAGE_CODE

            for part in picture_xml.partiter():
                if picture_xml.frame:
                    c = picture_xml.frame[0]
                    part['coords'] = [[p[0] - c[0], p[1] - c[1]] for p in part['coords']]
                if part.get('object', None) is not None:
                    _tags = set()
                    for objname in part['object'].split(','):
                        objname = objname.strip()
                        assert objname, 'Empty object name'
                        # str.capitalize() is wrong, because it also lowers letters
                        objname = objname[0].upper() + objname[1:]
                        tag, created = catalogue.models.Tag.objects.get_or_create(
                            slug=slughifi(objname), category='thing')
                        if created:
                            tag.name = objname
                            setattr(tag, 'name_%s' % lang, tag.name)
                            tag.sort_key = sortify(tag.name)
                            tag.save()
                        # thing_tags.add(tag)
                        area_data['things'][tag.slug] = {
                            'object': objname,
                            'coords': part['coords'],
                            }

                        _tags.add(tag)
                    area = PictureArea.rectangle(picture, 'thing', part['coords'])
                    area.save()
                    area.tags = _tags
                else:
                    _tags = set()
                    for motifs in part['themes']:
                        for motif in motifs.split(','):
                            tag, created = catalogue.models.Tag.objects.get_or_create(
                                slug=slughifi(motif), category='theme')
                            if created:
                                tag.name = motif
                                tag.sort_key = sortify(tag.name)
                                tag.save()
                            # motif_tags.add(tag)
                            _tags.add(tag)
                            area_data['themes'][tag.slug] = {
                                'theme': motif,
                                'coords': part['coords']
                                }

                    logging.debug("coords for theme: %s" % part['coords'])
                    area = PictureArea.rectangle(picture, 'theme', part['coords'])
                    area.save()
                    area.tags = _tags.union(picture_tags)

            picture.tags = picture_tags
            picture.areas_json = area_data

            if image_file is not None:
                img = image_file
            else:
                img = picture_xml.image_file()

            modified = cls.crop_to_frame(picture_xml, img)
            modified = cls.add_source_note(picture_xml, modified)

            picture.width, picture.height = modified.size

            modified_file = StringIO()
            modified.save(modified_file, format='JPEG', quality=95)
            # FIXME: hardcoded extension - detect from DC format or orginal filename
            picture.image_file.save(path.basename(picture_xml.image_path), File(modified_file))

            picture.xml_file.save("%s.xml" % picture.slug, File(xml_file))
            picture.save()
            tasks.generate_picture_html(picture.id)

        if close_xml_file:
            xml_file.close()
        if close_image_file:
            image_file.close()

        return picture

    @classmethod
    def crop_to_frame(cls, wlpic, image_file):
        img = Image.open(image_file)
        if wlpic.frame is None or wlpic.frame == [[0, 0], [-1, -1]]:
            return img
        img = img.crop(itertools.chain(*wlpic.frame))
        return img

    @staticmethod
    def add_source_note(wlpic, img):
        from PIL import ImageDraw, ImageFont
        from librarian import get_resource

        annotated = Image.new(img.mode, (img.size[0], img.size[1] + 40), (255, 255, 255))
        annotated.paste(img, (0, 0))
        annotation = Image.new('RGB', (img.size[0] * 3, 120), (255, 255, 255))
        ImageDraw.Draw(annotation).text(
            (30, 15),
            wlpic.picture_info.source_name,
            (0, 0, 0),
            font=ImageFont.truetype(get_resource("fonts/DejaVuSerif.ttf"), 75)
        )
        annotated.paste(annotation.resize((img.size[0], 40), Image.ANTIALIAS), (0, img.size[1]))
        return annotated

    # WTF/unused
    @classmethod
    def picture_list(cls, filter=None):
        """Generates a hierarchical listing of all pictures
        Pictures are optionally filtered with a test function.
        """

        pics = cls.objects.all().order_by('sort_key').only('title', 'slug', 'image_file')

        if filter:
            pics = pics.filter(filter).distinct()

        pics_by_author = SortedDict()
        orphans = []
        for tag in catalogue.models.Tag.objects.filter(category='author'):
            pics_by_author[tag] = []

        for pic in pics.iterator():
            authors = list(pic.authors().only('pk'))
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

    def pretty_title(self, html_links=False):
        names = [(tag.name, tag.get_absolute_url()) for tag in self.authors().only('name', 'category', 'slug')]
        names.append((self.title, self.get_absolute_url()))

        if html_links:
            names = ['<a href="%s">%s</a>' % (tag[1], tag[0]) for tag in names]
        else:
            names = [tag[0] for tag in names]
        return ', '.join(names)

    def related_themes(self):
        return catalogue.models.Tag.objects.usage_for_queryset(
            self.areas.all(), counts=True).filter(category__in=('theme', 'thing'))

    def flush_includes(self, languages=True):
        if not languages:
            return
        if languages is True:
            languages = [lc for (lc, _ln) in settings.LANGUAGES]
        flush_ssi_includes([
            template % (self.pk, lang)
            for template in [
                '/katalog/p/%d/short.%s.html',
                '/katalog/p/%d/mini.%s.html',
                ]
            for lang in languages
            ])
