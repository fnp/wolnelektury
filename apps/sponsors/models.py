from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from sponsors.fields import JSONField


class Sponsor(models.Model):
    name = models.CharField(_('name'), max_length=120)
    _description = models.CharField(_('description'), blank=True, max_length=255)
    logo = models.ImageField(_('logo'), upload_to='sponsors/sponsor/logo')
    url = models.URLField(_('url'), blank=True, verify_exists=False)
    
    def __unicode__(self):
        return self.name

    def description(self):
        if len(self._description):
            return self._description
        else:
            return self.name


class SponsorPage(models.Model):
    name = models.CharField(_('name'), max_length=120)
    column_width = models.PositiveIntegerField(_('column width'), default=200)
    sponsors = JSONField(_('sponsors'), default={})
    _html = models.TextField(blank=True, editable=False)
    
    def populated_sponsors(self):
        result = []
        for column in self.get_sponsors_value():
            result_group = {'name': column['name'], 'sponsors': []}
            sponsor_objects = Sponsor.objects.in_bulk(column['sponsors'])
            for sponsor_pk in column['sponsors']:
                try:
                    result_group['sponsors'].append(sponsor_objects[sponsor_pk])
                except KeyError:
                    pass
            result.append(result_group)
        return result
    
    def html(self):
        return self._html
    html = property(fget=html)

    def save(self, *args, **kwargs):
        self._html = render_to_string('sponsors/page.html', {
            'column_width': self.column_width,
            'sponsors': self.populated_sponsors(),
        })
        return super(SponsorPage, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name

