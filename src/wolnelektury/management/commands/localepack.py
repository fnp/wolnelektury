# This file is part of Wolne Lektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Wolne Lektury. See NOTICE for more information.
#
import os
import shutil
import sys
import tempfile
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from wolnelektury.utils import makedirs
from .translation2po import get_languages


ROOT = settings.ROOT_DIR


def is_our_app(mod):
    return mod.__path__[0].startswith(ROOT)


class Locale(object):
    def save(self, output_directory, languages):
        pass

    def compile(self):
        pass

    def generate(self, languages):
        pass


def copy_f(frm, to):
    makedirs(os.path.dirname(to))
    shutil.copyfile(frm, to)


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
                copy_f(os.path.join(self.path, 'locale', lc, 'LC_MESSAGES', 'django.po'),
                       os.path.join(output_directory, lc, self.name + '.po'))

    def load(self, input_directory, languages):
        for lc in zip(*languages)[0]:
            if os.path.exists(os.path.join(input_directory, lc, self.name + '.po')):
                out = os.path.join(self.path, 'locale', lc, 'LC_MESSAGES', 'django.po')
                makedirs(os.path.dirname(out))
                copy_f(os.path.join(input_directory, lc, self.name + '.po'), out)
        self.compile()

    def compile(self):
        wd = os.getcwd()
        os.chdir(self.path)
        try:
            call_command('compilemessages', verbosity=0, settings='wolnelektury.settings')
        except:
            pass
        finally:
            os.chdir(wd)

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
                     load=True, lang=','.join(zip(*languages)[0]), poname=self.poname, keep_running=True)


SOURCES = []

for appn in settings.INSTALLED_APPS:
    app = __import__(appn)
    if is_our_app(app):
        try:
            SOURCES.append(AppLocale(app))
        except LookupError as e:
            print("no locales in %s" % app.__name__)

SOURCES.append(ModelTranslation('infopages', 'infopages_db'))


class Command(BaseCommand):
    help = 'Make a locale pack'

    def add_arguments(self, parser):
        parser.add_argument(
                '-l', '--load', help='load locales back to source',
                action='store_true', dest='load', default=False)
        parser.add_argument(
                '-c', '--compile', help='compile messages',
                action='store_true', dest='compile', default=False)
        parser.add_argument(
                '-g', '--generate', help='generate messages',
                action='store_true', dest='generate', default=False)
        parser.add_argument(
                '-L', '--lang', help='load just one language',
                dest='lang', default=None)
        parser.add_argument(
                '-d', '--directory', help='load from this directory',
                dest='directory', default=None)
        parser.add_argument(
                '-o', '--outfile', help='Resulting zip file',
                dest='outfile', default='./wl-locale.zip')
        parser.add_argument(
                '-m', '--merge', action='store_true',
                dest='merge', default=False,
                help='Use git to merge. Please use with clean working directory.')
        parser.add_argument(
                '-M', '--message', help='commit message',
                dest='message', default='New locale')

    def current_rev(self):
        return os.popen('git rev-parse HEAD').read()

    def current_branch(self):
        return os.popen("git branch |grep '^[*]' | cut -c 3-").read()

    def save(self, options):
        packname = options.get('outfile')
        packname_b = os.path.basename(packname).split('.')[0]
        fmt = '.'.join(os.path.basename(packname).split('.')[1:])

        if fmt != 'zip':
            raise NotImplementedError('Sorry. Only zip format supported at the moment.')

        tmp_dir = tempfile.mkdtemp('-wl-locale')
        out_dir = os.path.join(tmp_dir, packname_b)
        os.mkdir(out_dir)

        try:
            for lang in settings.LANGUAGES:
                os.mkdir(os.path.join(out_dir, lang[0]))

            for src in SOURCES:
                src.generate(settings.LANGUAGES)
                src.save(out_dir, settings.LANGUAGES)
                #                src.save(settings.LANGUAGES)

            # write out revision
            rev = self.current_rev()
            rf = open(os.path.join(out_dir, '.revision'), 'w')
            rf.write(rev)
            rf.close()

            cwd = os.getcwd()
            try:
                os.chdir(os.path.dirname(out_dir))
                self.system('zip -r %s %s' % (os.path.join(cwd, packname_b+'.zip'), os.path.basename(out_dir)))
            finally:
                os.chdir(cwd)
                # shutil.make_archive(packname_b, fmt, root_dir=os.path.dirname(out_dir),
                #                     base_dir=os.path.basename(out_dir))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def generate(self):
        for src in SOURCES:
            src.generate(settings.LANGUAGES)

    def load(self, options):
        langs = get_languages(options['lang'])

        for src in SOURCES:
            src.load(options['directory'], langs)

    def compile(self):
        for src in SOURCES:
            src.compile()

    def handle(self, **options):
        if options['load']:
            if not options['directory'] or not os.path.exists(options['directory']):
                print("Directory not provided or does not exist, please use -d")
                sys.exit(1)

            if options['merge']:
                self.merge_setup(options['directory'])
            self.load(options)
            if options['merge']:
                self.merge_finish(options['message'])
        elif options['generate']:
            self.generate()
        elif options['compile']:
            self.compile()
        else:
            self.save(options)

    merge_branch = 'wl-locale-merge'
    last_branch = None

    def merge_setup(self, directory):
        self.last_branch = self.current_branch()
        rev = open(os.path.join(directory, '.revision')).read()

        self.system('git checkout -b %s %s' % (self.merge_branch, rev))

    def merge_finish(self, message):
        self.system('git commit -a -m "%s"' % message.replace('"', '\\"'))
        self.system('git checkout %s' % self.last_branch)
        self.system('git merge -s recursive -X theirs %s' % self.merge_branch)
        self.system('git branch -d %s' % self.merge_branch)

    def system(self, fmt, *args):
        code = os.system(fmt % args)
        if code != 0:
            raise OSError('Command %s returned with exit code %d' % (fmt % args, code))
        return code
