# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
from django.db import models, transaction
import catalogue.models
from sorl.thumbnail import ImageField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from slugify import slugify

from catalogue.models.tag import prefetched_relations
from catalogue.utils import split_tags
from wolnelektury.utils import cached_render, clear_cached_renders
from io import BytesIO
import itertools
import json
import logging
import re

from PIL import Image

from newtagging import managers
from os import path


picture_storage = FileSystemStorage(location=path.join(
        settings.MEDIA_ROOT, 'pictures'),
        base_url=settings.MEDIA_URL + "pictures/")


class PictureArea(models.Model):
    picture = models.ForeignKey('picture.Picture', models.CASCADE, related_name='areas')
    area = models.TextField('obszar', default='{}', editable=False)
    kind = models.CharField(
        'typ', max_length=10, blank=False, null=False, db_index=True,
        choices=(('thing', 'przedmiot'), ('theme', 'motyw'))
    )

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags = managers.TagDescriptor(catalogue.models.Tag)
    tag_relations = GenericRelation(catalogue.models.Tag.intermediary_table_model)


class Picture(models.Model):
    """
    Picture resource.

    """
    title = models.CharField('tytuł', max_length=32767)
    slug = models.SlugField('slug', max_length=120, db_index=True, unique=True)
    sort_key = models.CharField('klucz sortowania', max_length=120, db_index=True, editable=False)
    sort_key_author = models.CharField(
        'klucz sortowania wg autora', max_length=120, db_index=True, editable=False, default='')
    created_at = models.DateTimeField('data utworzenia', auto_now_add=True, db_index=True)
    changed_at = models.DateTimeField('data zmiany', auto_now=True, db_index=True)
    xml_file = models.FileField('plik xml', upload_to="xml", storage=picture_storage)
    image_file = ImageField('plik obrazu', upload_to="images", storage=picture_storage)
    html_file = models.FileField('plik html', upload_to="html", storage=picture_storage)
    areas_json = models.TextField('obszary w JSON', default='{}', editable=False)
    extra_info = models.TextField('dodatkowa informacja', default='{}')
    culturepl_link = models.CharField(blank=True, max_length=240)
    wiki_link = models.CharField(blank=True, max_length=240)

    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)

    objects = models.Manager()
    tagged = managers.ModelTaggedItemManager(catalogue.models.Tag)
    tags = managers.TagDescriptor(catalogue.models.Tag)
    tag_relations = GenericRelation(catalogue.models.Tag.intermediary_table_model)

    class Meta:
        ordering = ('sort_key_author', 'sort_key')

        verbose_name = 'obraz'
        verbose_name_plural = 'obrazy'

    def __str__(self):
        return self.title
