# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import os
import time
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.db import models

import polib
import modeltranslation.models
from modeltranslation.translator import translator, NotRegistered


def metadata(language=''):
    "get metadata for PO, given language code"
    t = time.strftime('%Y-%m-%d %H:%M%z')

    return {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': settings.CONTACT_EMAIL,
        'POT-Creation-Date': '%s' % t,
        'PO-Revision-Date': '%s' % t,
        'Last-Translator': 'you <you@example.com>',
        'Language-Team': '%s' % dict(settings.LANGUAGES).get(language, language),
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        }


def make_po(language=''):
    "Create new POFile object for language code"
    po = polib.POFile()
    po.metadata = metadata(language)
    return po


def get_languages(langs):
    if not langs: return settings.LANGUAGES
    langs = langs.split(',')
    lm = dict(settings.LANGUAGES)
    return map(lambda l: (l, lm.get(l, l)), langs)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-d', '--directory', help='Specify which directory should hold generated PO files', dest='directory', default=''),
        make_option('-l', '--load', help='load locales back to source', action='store_true', dest='load', default=False),
        make_option('-L', '--language', help='locales to load', dest='lang', default=None),
        make_option('-n', '--poname', help='name of the po file [no extension]', dest='poname', default=None),
        make_option('-k', '--keep-running', help='keep running even when missing an input file', dest='keep_running', default=False, action='store_true'),
        )
    help = 'Export models from app to po files'
    args = 'app'

    def get_models(self, app):
        for mdname in dir(app.models):
            if mdname[0] == '_': continue
            md = getattr(app.models, mdname)
            try:
                assert issubclass(md, models.Model)
            except (AssertionError, TypeError):
                continue

            try:
                opts = translator.get_options_for_model(md)
            except NotRegistered:
                continue
            else:
                yield (md, opts)

    def handle(self, appname, **options):
        if not options['poname']: options['poname'] = appname
        app = __import__(appname)

        if options['load']:
            objects = {}
            modmod = {}
            for md, opts in self.get_models(app):
                if not md.__name__ in objects:
                    objects[md.__name__] = {}
                    modmod['model'] = md

            languages = get_languages(options['lang'])

            for lng in zip(*languages)[0]:
                pofile = os.path.join(options['directory'], lng, options['poname'] + '.po')
                if not os.path.exists(pofile):
                    if options['keep_running']:
                        continue
                    else:
                        raise OSError('%s po file: %s not found' % (appname, pofile))
                po = polib.pofile(pofile)
                for entry in po:
                    loc, _ignored = entry.occurrences[0]
                    _appname, modelname, fieldname, pk = loc.split('/')
                    try:
                        obj = objects[modelname][pk]
                    except KeyError:
                        obj = modmod['model'].objects.get(pk=pk)
                        objects[modelname][pk] = obj
                    setattr(obj, fieldname, entry.msgstr)

            for mod, objcs in objects.items():
                for o in objcs.values():
                    o.save()

        else:
            pofiles = {}
            for md, opts in self.get_models(app):
                for obj in md.objects.all().order_by('pk'):
                    for fld, locflds in opts.local_fields.items():
                        k = getattr(obj, '%s_%s' % (fld, settings.LANGUAGE_CODE)) or ''
                        for locfld in locflds:
                            cur_lang = locfld.language
                            try:
                                po = pofiles[cur_lang]
                            except:
                                po = make_po(cur_lang)
                                pofiles[cur_lang] = po
                            v = locfld.value_from_object(obj) or ''
                            entry = polib.POEntry(
                                msgid=k,
                                msgstr=v,
                                occurrences=[('%s/%s/%s/%s' % (appname, md.__name__, locfld.name, str(obj.pk)), 0)])
                            po.append(entry)

            directory = options['directory']
            for lng, po in pofiles.items():
                os.makedirs(os.path.join(directory, lng))
                po.save(os.path.join(directory, lng, '%s.po' % options['poname']))
