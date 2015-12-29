# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import cPickle
from datetime import datetime
from random import randint
from StringIO import StringIO

from django.core.files.base import ContentFile
from django.db import models
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

from jsonfield import JSONField
from catalogue.models import Book, Tag


class Poem(models.Model):
    slug = models.SlugField(_('slug'), max_length=120, db_index=True)
    text = models.TextField(_('text'))
    created_by = models.ForeignKey(User, null=True)
    created_from = JSONField(_('extra information'), null=True, blank=True)
    created_at = models.DateTimeField(_('creation date'), auto_now_add=True, editable=False)
    seen_at = models.DateTimeField(_('last view date'), auto_now_add=True, editable=False)
    view_count = models.IntegerField(_('view count'), default=1)

    try:
        f = open(settings.LESMIANATOR_PICKLE)
        global_dictionary = cPickle.load(f)
        f.close()
    except:
        global_dictionary = {}

    def visit(self):
        self.view_count += 1
        self.seen_at = datetime.utcnow().replace(tzinfo=utc)
        self.save()

    def __unicode__(self):
        return "%s (%s...)" % (self.slug, self.text[:20])

    @staticmethod
    def choose_letter(word, continuations):
        if word not in continuations:
            return u'\n'

        choices = sum((continuations[word][letter]
                       for letter in continuations[word]))
        r = randint(0, choices - 1)

        for letter in continuations[word]:
            r -= continuations[word][letter]
            if r < 0:
                return letter

    @classmethod
    def write(cls, continuations=None, length=3, min_lines=2, maxlen=1000):
        if continuations is None:
            continuations = cls.global_dictionary
        if not continuations:
            return ''

        letters = []
        word = u''

        finished_stanza_verses = 0
        current_stanza_verses = 0
        verse_start = True

        char_count = 0

        # do `min_lines' non-empty verses and then stop,
        # but let Lesmianator finish his last stanza.
        while finished_stanza_verses < min_lines and char_count < maxlen:
            letter = cls.choose_letter(word, continuations)
            letters.append(letter)
            word = word[-length + 1:] + letter
            char_count += 1

            if letter == u'\n':
                if verse_start:
                    finished_stanza_verses += current_stanza_verses
                    current_stanza_verses = 0
                else:
                    current_stanza_verses += 1
                    verse_start = True
            else:
                verse_start = False

        return ''.join(letters).strip()

    def get_absolute_url(self):
        return reverse('get_poem', kwargs={'poem': self.slug})


class Continuations(models.Model):
    pickle = models.FileField(_('Continuations file'), upload_to='lesmianator')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('content_type', 'object_id'), )

    def __unicode__(self):
        return "Continuations for: %s" % unicode(self.content_object)

    @staticmethod
    def join_conts(a, b):
        for pre in b:
            a.setdefault(pre, {})
            for post in b[pre]:
                a[pre].setdefault(post, 0)
                a[pre][post] += b[pre][post]
        return a

    @classmethod
    def for_book(cls, book, length=3):
        # count from this book only
        output = StringIO()
        wldoc = book.wldocument(parse_dublincore=False)
        output = wldoc.as_text(('raw-text',)).get_string()
        del wldoc

        conts = {}
        last_word = ''
        for letter in output.decode('utf-8').strip().lower():
            mydict = conts.setdefault(last_word, {})
            mydict.setdefault(letter, 0)
            mydict[letter] += 1
            last_word = last_word[-length+1:] + letter
        # add children
        return reduce(cls.join_conts,
                      (cls.get(child) for child in book.children.all().iterator()),
                      conts)

    @classmethod
    def for_set(cls, tag):
        books = Book.tagged_top_level([tag])
        cont_tabs = (cls.get(b) for b in books.iterator())
        return reduce(cls.join_conts, cont_tabs)

    @classmethod
    def get(cls, sth):
        object_type = ContentType.objects.get_for_model(sth)
        should_keys = set([sth.id])
        if isinstance(sth, Tag):
            should_keys = set(b.pk for b in Book.tagged.with_any((sth,)).iterator())
        try:
            obj = cls.objects.get(content_type=object_type, object_id=sth.id)
            if not obj.pickle:
                raise cls.DoesNotExist
            f = open(obj.pickle.path)
            keys, conts = cPickle.load(f)
            f.close()
            if set(keys) != should_keys:
                raise cls.DoesNotExist
            return conts
        except cls.DoesNotExist:
            if isinstance(sth, Book):
                conts = cls.for_book(sth)
            elif isinstance(sth, Tag):
                conts = cls.for_set(sth)
            else:
                raise NotImplementedError('Lesmianator continuations: only Book and Tag supported')

            c, created = cls.objects.get_or_create(content_type=object_type, object_id=sth.id)
            c.pickle.save(sth.slug+'.p', ContentFile(cPickle.dumps((should_keys, conts))))
            c.save()
            return conts


