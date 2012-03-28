
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from django.core.management import call_command

import os
import shutil
import tempfile

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
            shutil.copy2(os.path.join(input_directory, lc, self.name + '.po'),
                         os.path.join(self.path, 'locale', lc, 'LC_MESSAGES', 'django.po'))

    def generate(self, languages):
        os.chdir(self.path)
        print "in %s" % os.getcwd()
        try:
            call_command('makemessages', all=True)
        except:
            pass


class ModelTranslation(Locale):
    def __init__(self, appname):
        self.appname = appname

    def save(self, output_directory, languages):
        call_command('translation2po', self.appname, directory=output_directory)

    def load(self, input_directory, languages):
        call_command('translation2po', self.appname, directory=input_directory, load=True)


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


SOURCES = []

for appn in settings.INSTALLED_APPS:
    app = __import__(appn)
    if is_our_app(app):
        try:
            SOURCES.append(AppLocale(app))
        except LookupError, e:
            print "no locales in %s" % app

SOURCES.append(ModelTranslation('infopages'))
SOURCES.append(CustomLocale(os.path.dirname(allauth.__file__), name='contrib'))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-l', '--load', help='load locales back to source', action='store_true', dest='load', default=False),
        make_option('-o', '--outfile', help='Resulting zip file', dest='outfile', default='./wl-locale.zip'),
        )
    help = 'Make a locale pack'
    args = ''

    def handle(self, *a, **options):
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

            packname = options.get('outfile')
            packname_b = os.path.basename(packname).split('.')[0]
            fmt = '.'.join(os.path.basename(packname).split('.')[1:])
            shutil.make_archive(packname_b, fmt, root_dir=os.path.dirname(out_dir), base_dir=os.path.basename(out_dir))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
