from django.db import models
import catalogue.models
from django.db.models import permalink
from sorl.thumbnail import ImageField
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import SortedDict
from django.template.loader import render_to_string
from django.core.cache import get_cache
from catalogue.utils import split_tags
from django.utils.safestring import mark_safe
from fnpdjango.utils.text.slughifi import slughifi

from django.utils.translation import ugettext_lazy as _
from newtagging import managers
from os import path


picture_storage = FileSystemStorage(location=path.join(settings.MEDIA_ROOT, 'pictures'), base_url=settings.MEDIA_URL + "pictures/")


class Picture(models.Model):
    """
    Picture resource.

    """
    title       = models.CharField(_('title'), max_length=120)
    slug        = models.SlugField(_('slug'), max_length=120, db_index=True, unique=True)
    sort_key    = models.CharField(_('sort key'), max_length=120, db_index=True, editable=False)
    created_at  = models.DateTimeField(_('creation date'), auto_now_add=True, db_index=True)
    changed_at  = models.DateTimeField(_('creation date'), auto_now=True, db_index=True)
    xml_file    = models.FileField('xml_file', upload_to="xml", storage=picture_storage)
    image_file  = ImageField(_('image_file'), upload_to="images", storage=picture_storage)
    objects     = models.Manager()
    tagged      = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags        = managers.TagDescriptor(catalogue.models.Tag)

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
    def from_xml_file(cls, xml_file, image_file=None, overwrite=False):
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
        # class SimpleImageStore(object):
        #     def path(self_, slug, mime_type):
        #         """Returns the image file. Ignores slug ad mime_type."""
        #         return image_file

        if image_file is not None and not isinstance(image_file, File):
            image_file = File(open(image_file))
            close_image_file = True

        if not isinstance(xml_file, File):
            xml_file = File(open(xml_file))
            close_xml_file = True

        try:
            # use librarian to parse meta-data
            picture_xml = WLPicture.from_file(xml_file,
                                              image_store=ImageStore(picture_storage.path('images')))
                    # image_store=SimpleImageStore

            picture, created = Picture.objects.get_or_create(slug=picture_xml.slug)
            if not created and not overwrite:
                raise Picture.AlreadyExists('Picture %s already exists' % picture_xml.slug)

            picture.title = picture_xml.picture_info.title

            motif_tags = set()
            for part in picture_xml.partiter():
                for motif in part['themes']:
                    tag, created = catalogue.models.Tag.objects.get_or_create(slug=slughifi(motif), category='theme')
                    if created:
                        tag.name = motif
                        tag.sort_key = sortify(tag.name)
                        tag.save()
                    motif_tags.add(tag)

            picture.tags = catalogue.models.Tag.tags_from_info(picture_xml.picture_info) + \
                list(motif_tags)

            if image_file is not None:
                img = image_file
            else:
                img = picture_xml.image_file()

            # FIXME: hardcoded extension
            picture.image_file.save(path.basename(picture_xml.image_path), File(img))

            picture.xml_file.save("%s.xml" % picture.slug, File(xml_file))
            picture.save()
        finally:
            if close_xml_file:
                xml_file.close()
            if close_image_file:
                image_file.close()
        return picture

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

        cache_key = "Picture.short_html/%d" % (self.id)
        get_cache('permanent').delete(cache_key)

    def short_html(self):
        if self.id:
            cache_key = "Picture.short_html/%d" % (self.id)
            short_html = get_cache('permanent').get(cache_key)
        else:
            short_html = None

        if short_html is not None:
            return mark_safe(short_html)
        else:
            tags = self.tags.filter(category__in=('author', 'kind', 'epoch', 'genre'))
            tags = split_tags(tags)

            short_html = unicode(render_to_string('picture/picture_short.html',
                {'picture': self, 'tags': tags}))

            if self.id:
                get_cache('permanent').set(cache_key, short_html)
            return mark_safe(short_html)
