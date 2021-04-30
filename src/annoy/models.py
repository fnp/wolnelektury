from django.apps import apps
from django.conf import settings
from django.db import models
from django.template import Context, Template
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from .places import PLACES, PLACE_CHOICES, STYLES


class Banner(models.Model):
    place = models.SlugField(_('place'), choices=PLACE_CHOICES)
    style = models.CharField(
        _('style'), max_length=255, blank=True,
        choices=STYLES,
        help_text=_('Affects blackout.')
    )
    smallfont = models.BooleanField(_('small font'), default=False)
    action_label = models.CharField(
        _('action label'),
        max_length=255, blank=True,
        help_text=_('If empty, whole banner will serve as a link')
    )
    open_label = models.CharField(_('open label'), max_length=255, blank=True)
    close_label = models.CharField(_('close label'), max_length=255, blank=True)
    text = models.TextField(_('text'))
    image = models.FileField(_('image'), upload_to='annoy/banners/', blank=True)
    url = models.CharField(_('url'), max_length=1024)
    priority = models.PositiveSmallIntegerField(
        _('priority'), default=0,
        help_text=_('Banners with higher priority come first.'))
    since = models.DateTimeField(_('since'), null=True, blank=True)
    until = models.DateTimeField(_('until'), null=True, blank=True)
    show_members = models.BooleanField(_('show members'), default=False)
    staff_preview = models.BooleanField(_('staff preview'), default=False)

    class Meta:
        verbose_name = _('banner')
        verbose_name_plural = _('banners')
        ordering = ('place', '-priority',)

    def __str__(self):
        return self.text

    def get_text(self):
        return Template(self.text).render(Context())

    @classmethod
    def choice(cls, place, request):
        Membership = apps.get_model('club', 'Membership')

        if hasattr(request, 'annoy_banner_exempt'):
            return cls.objects.none()

        if settings.DEBUG:
            assert place in PLACES, f"Banner place `{place}` must be defined in annoy.places."

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

    @classmethod
    def get_all(cls, request):
        Membership = apps.get_model('club', 'Membership')
        if Membership.is_active_for(request.user) and not request.user.is_staff:
            return cls.objects.none()
        return cls.objects.all()


    def choose(self):
        return self.dynamictextinserttext_set.order_by('?').first()


class DynamicTextInsertText(models.Model):
    insert = models.ForeignKey(DynamicTextInsert, models.CASCADE)
    own_colors = models.BooleanField(default=False)
    background_color = models.CharField(max_length=10, blank=True)
    text_color = models.CharField(max_length=10, blank=True)
    text = models.TextField(_('text'))
    image = models.FileField(blank=True, upload_to='annoy/inserts/')
