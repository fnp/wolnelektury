# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


USED_POLLS_KEY = 'used_polls'


class Poll(models.Model):

    question = models.TextField('pytanie')
    slug = models.SlugField('slug')
    open = models.BooleanField('otwarta', default=False)

    class Meta:
        verbose_name = 'ankieta'
        verbose_name_plural = 'ankiety'

    def clean(self):
        if self.open and Poll.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
            raise ValidationError('Slug otwartej ankiety musi być unikalny')
        return super(Poll, self).clean()

    def __str__(self):
        return self.question[:100] + ' (' + self.slug + ')'

    def get_absolute_url(self):
        return reverse('poll', args=[self.slug])

    @property
    def vote_count(self):
        return self.items.all().aggregate(models.Sum('vote_count'))['vote_count__sum']

    def voted(self, session):
        return self.id in session.get(USED_POLLS_KEY, [])


class PollItem(models.Model):

    poll = models.ForeignKey(Poll, models.CASCADE, related_name='items')
    content = models.TextField('treść')
    vote_count = models.IntegerField('licznik głosów', default=0)

    class Meta:
        verbose_name = 'pozycja ankiety'
        verbose_name_plural = 'pozycje ankiety'

    def __str__(self):
        return self.content + ' @ ' + str(self.poll)

    @property
    def vote_ratio(self):
        return (float(self.vote_count) / self.poll.vote_count) * 100 if self.poll.vote_count else 0

    def vote(self, session):
        self.vote_count += 1
        self.save()
        session.setdefault(USED_POLLS_KEY, []).append(self.poll.id)
        session.save()
