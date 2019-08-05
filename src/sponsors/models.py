# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import json
import time
from io import BytesIO
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from PIL import Image

from django.core.files.base import ContentFile

THUMB_WIDTH = 120
THUMB_HEIGHT = 120


class Sponsor(models.Model):
    name = models.CharField(_('name'), max_length=120)
    _description = models.CharField(_('description'), blank=True, max_length=255)
    logo = models.ImageField(_('logo'), upload_to='sponsorzy/sponsor/logo')
    url = models.URLField(_('url'), blank=True)

    def __str__(self):
        return self.name

    def description(self):
        if len(self._description):
            return self._description
        else:
            return self.name


class SponsorPage(models.Model):
    name = models.CharField(_('name'), max_length=120)
    sponsors = models.TextField(_('sponsors'), default='{}')
    _html = models.TextField(blank=True, editable=False)
    sprite = models.ImageField(upload_to='sponsorzy/sprite', blank=True)

    def get_sponsors_json(self):
        return json.loads(self.sponsors or '[]')

    def populated_sponsors(self):
        result = []
        offset = 0
        for column in self.get_sponsors_json():
            result_group = {'name': column['name'], 'sponsors': []}
            sponsor_objects = Sponsor.objects.in_bulk(column['sponsors'])
            for sponsor_pk in column['sponsors']:
                try:
                    result_group['sponsors'].append((offset, sponsor_objects[sponsor_pk]))
                    offset -= THUMB_HEIGHT
                except KeyError:
                    pass
            result.append(result_group)
        return result

    def render_sprite(self):
        sponsor_ids = []
        for column in self.get_sponsors_json():
            sponsor_ids.extend(column['sponsors'])
        sponsors = Sponsor.objects.in_bulk(sponsor_ids)
        sprite = Image.new('RGBA', (THUMB_WIDTH, len(sponsors) * THUMB_HEIGHT))
        for i, sponsor_id in enumerate(sponsor_ids):
            simg = Image.open(sponsors[sponsor_id].logo.path)
            if simg.size[0] > THUMB_WIDTH or simg.size[1] > THUMB_HEIGHT:
                size = (
                    min(THUMB_WIDTH,
                        round(simg.size[0] * THUMB_HEIGHT / simg.size[1])),
                    min(THUMB_HEIGHT,
                        round(simg.size[1] * THUMB_WIDTH / simg.size[0]))
                )
                simg = simg.resize(size, Image.ANTIALIAS)
            sprite.paste(simg, (
                    round((THUMB_WIDTH - simg.size[0]) / 2),
                    round(i * THUMB_HEIGHT + (THUMB_HEIGHT - simg.size[1]) / 2),
                    ))
        imgstr = BytesIO()
        sprite.save(imgstr, 'png')

        if self.sprite:
            self.sprite.delete(save=False)
        self.sprite.save('sponsorzy/sprite/%s-%d.png' % (
            self.name, time.time()), ContentFile(imgstr.getvalue()), save=False)

    def html(self):
        return self._html
    html = property(fget=html)

    def save(self, *args, **kwargs):
        self.render_sprite()
        self._html = render_to_string('sponsors/page.html', {
            'sponsors': self.populated_sponsors(),
            'page': self
        })
        ret = super(SponsorPage, self).save(*args, **kwargs)
        cache.delete('sponsor_page:' + name)
        return ret

    def __str__(self):
        return self.name
