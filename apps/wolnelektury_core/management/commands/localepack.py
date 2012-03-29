
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from modeltranslation.management.commands.translation2po import get_languages

import os
import shutil
import tempfile
import sys

import allauth

ROOT = os.path.dirname(settings.PROJECT_DIR)


def is_our_app(mod):
    return mod.__path__[0].startswith(ROOT)


class Locale(object):
    def save(self, output_directory, languages):
        pass

    def generate(self, languages):
        pass


class AppLocale(Locale):
    def __init__(self, appmod):
        self.app = appmod
        if not os.path.exists(os.path.join(self.path, 'locale')):
            raise LookupError('No locale for app %s' % appmod)

    @property
    def path(self):
        return self.app.__path__[0]

    @property
    def name(self):
        return self.app.__name__

    def save(self, output_directory, languages):
        for lc in languages:
            lc = lc[0]
            if os.path.exists(os.path.join(self.path, 'locale', lc)):
                shutil.copy2(os.path.join(self.path, 'locale', lc, 'LC_MESSAGES', 'django.po'),
                         os.path.join(output_directory, lc, self.name + '.po'))

    def load(self, input_directory, languages):
        for lc in zip(*languages)[0]:
            if os.path.exists(os.path.join(input_directory, lc, self.name + '.po')):
                shutil.copy2(os.path.join(input_directory, lc, self.name + '.po'),
                             os.path.join(self.path, 'locale', lc, 'LC_MESSAGES', 'django.po'))

    def generate(self, languages):
        wd = os.getcwd()
        os.chdir(self.path)
        try:
            call_command('makemessages', all=True)
        except:
            pass
        finally:
            os.chdir(wd)


class ModelTranslation(Locale):
    def __init__(self, appname, poname=None):
        self.appname = appname
        self.poname = poname and poname or appname

    def save(self, output_directory, languages):
        call_command('translation2po', self.appname, directory=output_directory, poname=self.poname)

    def load(self, input_directory, languages):
        call_command('translation2po', self.appname, directory=input_directory,
                     load=True, lang=','.join(zip(*languages)[0]), poname=self.poname)


class CustomLocale(Locale):
    def __init__(self, app_dir,
                 config=os.path.join(ROOT, "babel.cfg"),
                 out_file=os.path.join(ROOT, 'wolnelektury/locale-contrib/django.pot'),
                 name=None):
        self.app_dir = app_dir
        self.config = config
        self.out_file = out_file
        self.name = name

    def generate(self, languages):
        os.system('pybabel extract -F "%s" -o "%s" "%s"' % (self.config, self.out_file, self.app_dir))
        os.system('pybabel update -D django -i %s -d %s' % (self.out_file, os.path.dirname(self.out_file)))

    def po_file(self, language):
        d = os.path.dirname(self.out_file)
        n = os.path.basename(self.out_file).split('.')[0]
        return os.path.join(d, language, 'LC_MESSAGES', n + '.po')

    def save(self, output_directory, languages):
        for lc in zip(*languages)[0]:
            if os.path.exists(self.po_file(lc)):
                shutil.copy2(self.po_file(lc),
                             os.path.join(output_directory, lc, self.name + '.po'))

    def load(self, input_directory, languages):
        for lc in zip(*languages)[0]:
            shutil.copy2(os.path.join(input_directory, lc, self.name + '.po'),
                         self.po_file(lc))
        os.system('pybabel compile -D django -d %s' % os.path.dirname(self.out_file))


SOURCES = []

for appn in settings.INSTALLED_APPS:
    app = __import__(appn)
    if is_our_app(app):
        try:
            SOURCES.append(AppLocale(app))
        except LookupError, e:
            print "no locales in %s" % app.__name__

SOURCES.append(ModelTranslation('infopages', 'infopages_db'))
SOURCES.append(CustomLocale(os.path.dirname(allauth.__file__), name='contrib'))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-l', '--load', help='load locales back to source', action='store_true', dest='load', default=False),
        make_option('-L', '--lang', help='load just one language', dest='lang', default=None),
        make_option('-d', '--directory', help='load from this directory', dest='directory', default=None),
        make_option('-o', '--outfile', help='Resulting zip file', dest='outfile', default='./wl-locale.zip'),
        make_option('-m', '--merge', help='Use git to merge. Please use with clean working directory.', dest='merge', default=False),
        )
    help = 'Make a locale pack'
    args = ''

    def save(self, options):
        tmp_dir = tempfile.mkdtemp('-wl-locale')
        out_dir = os.path.join(tmp_dir, 'wl-locale')
        os.mkdir(out_dir)

        try:
            for lang in settings.LANGUAGES:
                os.mkdir(os.path.join(out_dir, lang[0]))

            for src in SOURCES:
                src.generate(settings.LANGUAGES)
                src.save(out_dir, settings.LANGUAGES)
                #                src.save(settings.LANGUAGES)

            # write out revision
            rev = os.popen('git rev-parse HEAD').read()
            rf = open(os.path.join(out_dir, '.revision'), 'w')
            rf.write(rev)
            rf.close()

            packname = options.get('outfile')
            packname_b = os.path.basename(packname).split('.')[0]
            fmt = '.'.join(os.path.basename(packname).split('.')[1:])
            shutil.make_archive(packname_b, fmt, root_dir=os.path.dirname(out_dir), base_dir=os.path.basename(out_dir))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def load(self, options):
        if not options['directory'] or not os.path.exists(options['directory']):
            print "Directory not provided or does not exist, please use -d"
            sys.exit(1)

        langs = get_languages(options['lang'])

        for src in SOURCES:
            src.load(options['directory'], langs)

    def handle(self, *a, **options):
        if options['load']:
            self.load(options)
        else:
            self.save(options)
