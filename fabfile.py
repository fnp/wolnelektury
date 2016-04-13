# -*- coding: utf-8 -*-
from fnpdeploy import *

try:
    from fabfile_local import *
except ImportError:
    pass


env.project_name = 'wolnelektury'


class ManageTask(Task):
    def __init__(self, name, params='', **kwargs):
        super(ManageTask, self).__init__(**kwargs)
        self.name = name
        self.params = params

    def run(self):
        require('app_path', 'project_name')
        with cd(get_django_root_path('current')):
            run('source %(ve)s/bin/activate && python manage.py %(task)s %(params)s' % {
                've': env.ve,
                'task': self.name,
                'params': self.params,
            }, pty=True)


class Memcached(Service):
    def run(self):
        print '>>> memcached: restart'
        sudo('service memcached restart', shell=False)


@task
def production():
    env.hosts = ['giewont.icm.edu.pl']
    env.user = 'lektury'
    env.app_path = '/srv/wolnelektury.pl'
    env.django_root_path = 'src'
    env.requirements_file = 'requirements/requirements.txt'
    env.pre_collectstatic = [
        ManageTask('update_counters'),
        ManageTask('localepack', '-c'),
    ]
    env.services = [
        Supervisord('wolnelektury'),
        Supervisord('wolnelektury.celery'),
        Memcached(),
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
        ManageTask('update_counters'),
        ManageTask('localepack', '-c'),
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
