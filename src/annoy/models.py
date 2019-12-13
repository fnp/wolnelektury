from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from .places import PLACES, PLACE_CHOICES


class Banner(models.Model):
    place = models.SlugField(choices=PLACE_CHOICES)
    action_label = models.CharField(
        max_length=255, blank=True,
        help_text=_('')
    )
    open_label = models.CharField(max_length=255, blank=True)
    close_label = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    url = models.CharField(max_length=1024)
    priority = models.PositiveSmallIntegerField(default=0)
    since = models.DateTimeField(null=True, blank=True)
    until = models.DateTimeField(null=True, blank=True)
    show_members = models.BooleanField(default=False)
    staff_preview = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('banner')
        verbose_name_plural = _('banners')
        ordering = ('place', '-priority',)

    def __str__(self):
        return self.text

    @classmethod
    def choice(cls, place, request):
        Membership = apps.get_model('club', 'Membership')

        if hasattr(request, 'annoy_banner_exempt'):
            return cls.objects.none()
        
        if settings.DEBUG:
            assert place in PLACES, "Banner place `{}` must be defined in annoy.places.".format(place)

        n = now()
        banners = cls.objects.filter(
            place=place
        ).exclude(
            since__gt=n
        ).exclude(
            until__lt=n
        ).order_by('-priority', '?')

        if not request.user.is_staff:
            banners = banners.filter(staff_preview=False)

        if request:
            if Membership.is_active_for(request.user):
                banners = banners.filter(show_members=True)
        return banners
        
        
class DynamicTextInsert(models.Model):
    paragraphs = models.IntegerField(_('pararaphs'))
    url = models.CharField(max_length=1024)

    class Meta:
        verbose_name = _('dynamic insert')
        verbose_name_plural = _('dynamic inserts')
        ordering = ('paragraphs', )

    def __str__(self):
        return str(self.paragraphs)

    def choose(self):
        return self.dynamictextinserttext_set.order_by('?').first()


class DynamicTextInsertText(models.Model):
    insert = models.ForeignKey(DynamicTextInsert, models.CASCADE)
    background_color = models.CharField(max_length=10, blank=True)
    text_color = models.CharField(max_length=10, blank=True)
    text = models.TextField(_('text'))
    image = models.FileField(blank=True)
