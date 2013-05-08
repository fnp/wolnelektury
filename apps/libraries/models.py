from django.db import models
from django.utils.translation import ugettext_lazy as _

class Library(models.Model):
    """Represent a single library in the libraries dictionary"""

    name = models.CharField(_('name'), max_length = 120, blank = True)
    url = models.CharField(_('url'), max_length = 120, blank = True)
    description = models.TextField(_('description'), blank = True)

    class Meta:
        verbose_name = _('library')
        verbose_name_plural = _('libraries')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('infopage', [self.slug])
