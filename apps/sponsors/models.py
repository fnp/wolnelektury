from django.db import models
from django.utils.translation import ugettext_lazy as _


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


class SponsorGroup(models.Model):
    name = models.CharField(_('name'), max_length=120)
    order = models.IntegerField(_('order'), default=0)
    column_width = models.PositiveIntegerField(_('column width'))
    sponsor_ids = models.CommaSeparatedIntegerField(_('sponsors'), max_length=255)
    
    def sponsors(self):
        ids = [int(pk) for pk in self.sponsor_ids.split(',')]
        result = Sponsor.objects.in_bulk(ids)
        return [result[pk] for pk in ids]
    sponsors.changes_data = False
    
    def __unicode__(self):
        return self.name

