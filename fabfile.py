from fnpdeploy import *
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
    env.django_root_path = 'src'
    env.requirements_file = 'requirements/requirements.txt'
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
