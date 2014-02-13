# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse


USED_POLLS_KEY = 'used_polls'


class Poll(models.Model):

    question = models.TextField(_('question'))
    slug = models.SlugField(_('slug'))
    open = models.BooleanField(_('open'), default=False)

    class Meta:
        verbose_name = _('Poll')
        verbose_name_plural = _('Polls')

    def clean(self):
        if self.open and Poll.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
            raise ValidationError(_('Slug of an open poll needs to be unique'))
        return super(Poll, self).clean()

    def __unicode__(self):
        return self.question[:100] + ' (' + self.slug + ')'

    def get_absolute_url(self):
        return reverse('poll', args=[self.slug])

    @property
    def vote_count(self):
        return self.items.all().aggregate(models.Sum('vote_count'))['vote_count__sum']

    def voted(self, session):
        return self.id in session.get(USED_POLLS_KEY, set())


class PollItem(models.Model):

    poll = models.ForeignKey(Poll, related_name='items')
    content = models.TextField(_('content'))
    vote_count = models.IntegerField(_('vote count'), default=0)

    class Meta:
        verbose_name = _('vote item')
        verbose_name_plural = _('vote items')

    def __unicode__(self):
        return self.content + ' @ ' + unicode(self.poll)

    @property
    def vote_ratio(self):
        return (float(self.vote_count) / self.poll.vote_count) * 100 if self.poll.vote_count else 0

    def vote(self, session):
        self.vote_count = self.vote_count + 1
        self.save()
        session.setdefault(USED_POLLS_KEY, set()).add(self.poll.id)
        session.save()
