# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from collections import OrderedDict
import json
from collections import namedtuple
from django.core.files.storage import storages
from django.db import models
from slugify import slugify
import mutagen


def _file_upload_to(i, _n):
    name = i.book.slug
    if i.index:
        name += f'_{i.index:03d}'
    if i.part_name:
        name += f'_' + slugify(i.part_name)
    ext = i.ext()
    return f'book/{ext}/{name}.{ext}'


def get_storage():
    return storages['bookmedia']


class BookMedia(models.Model):
    """Represents media attached to a book."""
    FileFormat = namedtuple("FileFormat", "name ext")
    formats = OrderedDict([
        ('mp3', FileFormat(name='MP3', ext='mp3')),
        ('ogg', FileFormat(name='Ogg Vorbis', ext='ogg')),
        ('daisy', FileFormat(name='DAISY', ext='daisy.zip')),
        ('audio.epub', FileFormat(name='EPUB+audio', ext='audio.epub')),
        ('sync', FileFormat(name='sync', ext='sync.txt')),
    ])
    format_choices = [(k, 'plik %s' % t.name) for k, t in formats.items()]

    type = models.CharField('typ', db_index=True, choices=format_choices, max_length=20)
    name = models.CharField('nazwa', max_length=512)
    part_name = models.CharField('nazwa części', default='', blank=True, max_length=512)
    index = models.IntegerField('indeks', default=0)
    file = models.FileField('plik', max_length=600, upload_to=_file_upload_to, storage=get_storage)
    file_size = models.IntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField('data utworzenia', auto_now_add=True, editable=False, db_index=True)
    project_description = models.CharField(max_length=2048, blank=True)
    project_icon = models.CharField(max_length=2048, blank=True)
    extra_info = models.TextField('dodatkowe informacje', default='{}', editable=False)
    book = models.ForeignKey('Book', models.CASCADE, related_name='media')
    source_sha1 = models.CharField(null=True, blank=True, max_length=40, editable=False)

    def __str__(self):
        return self.file.name.split("/")[-1]

    class Meta:
        ordering = ('type', 'index')
        verbose_name = 'media książki'
        verbose_name_plural = 'media książek'
        app_label = 'catalogue'

    def get_extra_info_json(self):
        return json.loads(self.extra_info or '{}')

    def get_nice_filename(self):
        parts_count = 1 + type(self).objects.filter(book=self.book, type=self.type).exclude(pk=self.pk).count()

        name = self.book.slug
        if parts_count > 0:
            name += f'_{self.index:03d}'
        if self.part_name:
            name += f'_' + slugify(self.part_name)
        ext = self.ext()
        return f'{name}.{ext}'

    def set_file(self, content, parts_count=None):
        if not parts_count:
            parts_count = 1 + type(self).objects.filter(book=self.book, type=self.type).exclude(pk=self.pk).count()
        if parts_count == 1:
            self.name = self.book.pretty_title()
        else:
            no = ('%02d' if parts_count < 100 else '%03d') % self.index
            self.name = '%s. %s' % (no, self.book.pretty_title())
            if self.part_name:
                self.name += ', ' + self.part_name

        if self.type in ('mp3', 'ogg'):
            try:
                audio = mutagen.File(content)
                self.duration = audio.info.length
            except (mutagen.MutagenError, AttributeError):
                self.extra_info = '{}'
                self.duration = None
                self.source_sha1 = None
            else:
                self.extra_info = json.dumps(
                    self.read_meta(audio, self.type))
                self.source_sha1 = self.read_source_sha1(audio, self.type)
        self.file_size = content.size
        self.file.save(None, content)
        self.book.update_narrators()
        self.book.update_has_audio()

    @staticmethod
    def read_meta(audio, file_type):
        """
            Reads some metadata from the audiobook.
        """
        tags = audio.tags
        if not tags:
            return {}
        artist_name = director_name = project = funded_by = license = ''
        if file_type == 'mp3':
            artist_name = ', '.join(', '.join(tag.text) for tag in tags.getall('TPE1'))
            director_name = ', '.join(', '.join(tag.text) for tag in tags.getall('TPE3'))
            license = ', '.join(tag.url for tag in tags.getall('WCOP'))
            project = ", ".join([
                t.data.decode('utf-8') for t in tags.getall('PRIV')
                if t.owner == 'wolnelektury.pl?project'])
            funded_by = ", ".join([
                t.data.decode('utf-8') for t in tags.getall('PRIV')
                if t.owner == 'wolnelektury.pl?funded_by'])
        elif file_type == 'ogg':
            artist_name = ', '.join(tags.get('artist', []))
            director_name = ', '.join(tags.get('conductor', []))
            license = ', '.join(tags.get('license', []))
            project = ", ".join(tags.get('project', []))
            funded_by = ", ".join(tags.get('funded_by', []))
        else:
            return {}
        return {'artist_name': artist_name, 'director_name': director_name,
                'project': project, 'funded_by': funded_by, 'license': license}

    def ext(self):
        return self.formats[self.type].ext

    @staticmethod
    def read_source_sha1(audio, filetype):
        """
            Reads source file SHA1 from audiobok metadata.
        """
        if not audio.tags:
            return None
        if filetype == 'mp3':
            try:
                return [t.data.decode('utf-8') for t in audio.tags.getall('PRIV')
                        if t.owner == 'wolnelektury.pl?flac_sha1'][0]
            except IndexError:
                return None
        elif filetype == 'ogg':
            try:
                return audio.tags.get('flac_sha1', [None])[0]
            except IndexError:
                return None
        else:
            return None

    @property
    def director(self):
        return self.get_extra_info_json().get('director_name', None)

    @property
    def artist(self):
        return self.get_extra_info_json().get('artist_name', None)

    def file_url(self):
        return self.file.url
