import hashlib
import json
from django.apps import apps
from django.conf import settings
from django.db import models
from django.template import Context, Template
from django.utils.timezone import now
from .places import PLACES, PLACE_CHOICES, STYLES


class Banner(models.Model):
    place = models.SlugField('miejsce', choices=PLACE_CHOICES)
    style = models.CharField(
        'styl', max_length=255, blank=True,
        choices=STYLES,
        help_text='Dotyczy blackoutu.'
    )
    smallfont = models.BooleanField('mały font', default=False)
    text_color = models.CharField(max_length=10, blank=True)
    background_color = models.CharField(max_length=10, blank=True)
    action_label = models.CharField(
        'etykieta akcji',
        max_length=255, blank=True,
        help_text='Jeśli pusta, cały banner będzie służył jako link.'
    )
    open_label = models.CharField('etykieta otwierania', max_length=255, blank=True)
    close_label = models.CharField('etykieta zamykania', max_length=255, blank=True)
    text = models.TextField('tekst')
    image = models.FileField('obraz', upload_to='annoy/banners/', blank=True)
    url = models.CharField('URL', max_length=1024)
    priority = models.PositiveSmallIntegerField(
        'priorytet', default=0,
        help_text='Bannery z wyższym priorytetem mają pierwszeństwo.')
    since = models.DateTimeField('od', null=True, blank=True)
    until = models.DateTimeField('do', null=True, blank=True)
    target = models.IntegerField('cel', null=True, blank=True)
    progress = models.IntegerField('postęp', null=True, blank=True)
    show_members = models.BooleanField('widoczny dla członków klubu', default=False)
    staff_preview = models.BooleanField('podgląd tylko dla zespołu', default=False)
    only_authenticated = models.BooleanField('tylko dla zalogowanych', default=False)

    class Meta:
        verbose_name = 'banner'
        verbose_name_plural = 'bannery'
        ordering = ('place', '-priority',)

    def __str__(self):
        return self.text

    def get_text(self):
        return Template(self.text).render(Context())

    @classmethod
    def choice(cls, place, request, exemptions=True):
        Membership = apps.get_model('club', 'Membership')

        if exemptions and hasattr(request, 'annoy_banner_exempt'):
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

        if not request.user.is_authenticated:
            banners = banners.filter(only_authenticated=False)

        if not request.user.is_staff:
            banners = banners.filter(staff_preview=False)

        if Membership.is_active_for(request.user):
            banners = banners.filter(show_members=True)

        return banners

    @property
    def progress_percent(self):
        if not self.target:
            return 0
        return (self.progress or 0) / self.target * 100

    def update_progress(self):
        # Total of new payments during the action.
        # This definition will need to change for longer timespans.
        if not self.since or not self.until or not self.target:
            return
        Schedule = apps.get_model('club', 'Schedule')
        self.progress = Schedule.objects.filter(
            payed_at__gte=self.since,
            payed_at__lte=self.until,
        ).aggregate(c=models.Sum('amount'))['c']
        self.save(update_fields=['progress'])

    @classmethod
    def update_all_progress(cls):
        for obj in cls.objects.exclude(target=None):
            obj.update_progress()


class DynamicTextInsert(models.Model):
    paragraphs = models.IntegerField('akapity')
    url = models.CharField(max_length=1024)

    class Meta:
        verbose_name = 'dynamiczna wstawka'
        verbose_name_plural = 'dynamiczne wstawki'
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
    text = models.TextField('tekst')
    image = models.FileField(blank=True, upload_to='annoy/inserts/')


class MediaInsertSet(models.Model):
    file_format = models.CharField(max_length=8, choices=[
        ('epub', 'epub'),
        ('mobi', 'mobi'),
        ('pdf', 'pdf'),
        ])
    etag = models.CharField(max_length=64, blank=True)

    def update_etag(self):
        self.etag = hashlib.sha1(json.dumps(self.get_texts()).encode('utf-8')).hexdigest()
        self.save(update_fields=['etag'])

    def get_texts(self):
        return [t.text for t in self.mediainserttext_set.all()]

    @classmethod
    def get_for_format(cls, file_format):
        return cls.objects.filter(file_format=file_format).first()

    @classmethod
    def get_texts_for(cls, file_format):
        self = cls.get_for_format(file_format)
        if self is None:
            return []
        return self.get_texts()


class MediaInsertText(models.Model):
    media_insert_set = models.ForeignKey(MediaInsertSet, models.CASCADE)
    ordering = models.IntegerField()
    text = models.TextField()

    class Meta:
        ordering = ('ordering',)
