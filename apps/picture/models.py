from django.db import models
import catalogue.models
from catalogue.fields import OverwritingFileField
from django.conf import settings
from django.core.files.storage import FileSystemStorage
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
    image_file  = models.FileField(_('image_file'), upload_to="images", storage=picture_storage)
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

        return ret

    def __unicode__(self):
        return self.title

    @classmethod
    def from_xml_file(cls, xml_file, images_path=None, overwrite=False):
        """
        Import xml and it's accompanying image file.
        """
        from django.core.files import File
        from librarian.picture import WLPicture
        close_xml_file = False

        if not isinstance(xml_file, File):
            xml_file = File(open(xml_file))
            close_xml_file = True
        try:
            # use librarian to parse meta-data
            picture_xml = WLPicture.from_file(xml_file)

            picture, created = Picture.objects.get_or_create(slug=picture_xml.slug)
            if not created and not overwrite:
                raise Picture.AlreadyExists('Picture %s already exists' % picture_xml.slug)

            picture.title = picture_xml.picture_info.title

            picture.tags = catalogue.models.Tag.tags_from_info(picture_xml.picture_info)

            img = picture_xml.image_file()
            try:
                picture.image_file.save(path.basename(picture_xml.image_path), File(img))
            finally:
                img.close()

            picture.xml_file.save("%s.xml" % picture.slug, File(xml_file))
            picture.save()
        finally:
            if close_xml_file:
                xml_file.close()
        return picture
