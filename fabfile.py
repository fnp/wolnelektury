# -*- coding: utf-8 -*-
from fnpdeploy import *

try:
    from fabfile_local import *
except ImportError:
    pass


env.project_name = 'wolnelektury'


def update_counters():
    print '>>> updating counters'
    require('app_path', 'project_name')
    with cd(get_django_root_path('current')):
        run('%(ve)s/bin/python manage.py update_counters' % env, pty=True)


def compile_messages():
    print '>>> compiling messages'
    require('app_path', 'project_name')
    with cd(get_django_root_path('current')):
        run('source %(ve)s/bin/activate && python manage.py localepack -c' % env, pty=True)


@task
def production():
    env.hosts = ['giewont.icm.edu.pl']
    env.user = 'lektury'
    env.app_path = '/srv/wolnelektury.pl'
    env.django_root_path = 'src'
    env.requirements_file = 'requirements/requirements.txt'
    env.pre_collectstatic = [
        update_counters,
        compile_messages,
    ]
    env.services = [
        Supervisord('wolnelektury'),
        Supervisord('wolnelektury.celery'),
    ]


@task
def beta():
    env.hosts = ['giewont.icm.edu.pl']
    env.user = 'lektury'
    env.app_path = '/srv/wolnelektury.pl/beta'
    env.ve = '/srv/wolnelektury.pl/ve'
    env.django_root_path = 'src'
    env.requirements_file = 'requirements/requirements.txt'
    env.pre_collectstatic = [
        update_counters,
        compile_messages,
    ]
    env.services = [
        Supervisord('beta'),
    ]


@task
def staging():
    env.hosts = ['san.nowoczesnapolska.org.pl:2223']
    env.user = 'staging'
    env.app_path = '/home/staging/wolnelektury.pl'
    env.services = [
        DebianGunicorn('wolnelektury'),
    ]
