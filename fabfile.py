from fnpdjango.deploy import *
try:
    from fabfile_local import *
except ImportError:
    pass


env.project_name = 'wolnelektury'


@task
def production():
    env.hosts = ['giewont.icm.edu.pl']
    env.user = 'lektury'
    env.app_path = '/srv/wolnelektury.pl'
    env.services = [
        Supervisord('wolnelektury.gunicorn'),
        Supervisord('celery.wolnelektury:'),
    ]


@task
def staging():
    env.hosts = ['san.nowoczesnapolska.org.pl:2223']
    env.user = 'staging'
    env.app_path = '/home/staging/wolnelektury.pl'
    env.services = [
        DebianGunicorn('wolnelektury'),
    ]
