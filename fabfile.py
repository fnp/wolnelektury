from __future__ import with_statement # needed for python 2.5
from fabric.api import *
from fabric.contrib import files
from fabric.context_managers import path

import os


# ==========
# = Config =
# ==========
# Globals
env.project_name = 'wolnelektury'
env.use_south = True

# Servers
def staging():
    """Use staging server"""
    env.hosts = ['stigma.nowoczesnapolska.org.pl:2222']
    env.user = 'platforma'
    env.path = '/var/services/wolnelektury'
    env.python = '/usr/bin/python'
    env.virtualenv = '/usr/bin/virtualenv'
    env.pip = '/usr/bin/pip'

def production():
    """Use production server"""
    env.hosts = ['wolnelektury.pl']
    env.user = 'lektury'
    env.path = '/srv/wolnelektury.pl'
    env.python = '/usr/bin/python'
    env.virtualenv = '/usr/bin/virtualenv'
    env.pip = 've/bin/pip'
    env.restart_webserver = restart_gunicorn_debian

# =========
# = Tasks =
# =========
def test():
    "Run the test suite and bail out if it fails"
    require('hosts', 'path', provided_by=[staging, production])
    result = run('cd %(path)s/%(project_name)s; %(python)s manage.py test' % env)

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment. virtualenv and pip should be already installed.
    """
    require('hosts', 'path', provided_by=[staging, production])

    run('mkdir -p %(path)s; cd %(path)s; %(virtualenv)s .;' % env, pty=True)
    run('cd %(path)s; mkdir releases; mkdir shared; mkdir packages;' % env, pty=True)
    run('cd %(path)s/releases; ln -s . current; ln -s . previous' % env, pty=True)
    deploy()

def deploy():
    """
    Deploy the latest version of the site to the servers,
    install any required third party modules,
    install the virtual host and then restart the webserver
    """
    require('hosts', 'path', provided_by=[staging, production])

    import time
    env.release = time.strftime('%Y-%m-%dT%H%M')

    upload_tar_from_git()
    upload_wsgi_script()
    upload_vhost_sample()
    upload_celery_conf()
    install_requirements()
    copy_localsettings()
    symlink_current_release()
    migrate()
    collectstatic()
    restart_webserver()
    restart_celery()

def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', 'path', provided_by=[localhost,webserver])
    env.version = version
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;', pty=True)
        run('ln -s %(version)s releases/current' % env, pty=True)
    restart_webserver()
    restart_celery()

def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[staging, production])
    require('path')
    with cd(env.path):
        run('mv releases/current releases/_previous;', pty=True)
        run('mv releases/previous releases/current;', pty=True)
        run('mv releases/_previous releases/previous;', pty=True)
    restart_webserver()
    restart_celery()


# =====================================================================
# = Helpers. These are called by other functions rather than directly =
# =====================================================================
def upload_tar_from_git():
    "Create an archive from the current Git branch and upload it"
    print '>>> upload tar from git'
    require('release', provided_by=[deploy])
    local('git-archive-all.sh --format tar %(release)s.tar' % env)
    local('gzip %(release)s.tar' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env, pty=True)
    run('mkdir -p %(path)s/packages' % env, pty=True)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env, pty=True)
    local('rm %(release)s.tar.gz' % env)

def upload_vhost_sample():
    "Create and upload Apache virtual host configuration sample"
    print ">>> upload vhost sample"
    files.upload_template('%(project_name)s.vhost.template' % env, '%(path)s/%(project_name)s.vhost.sample' % env, context=env)

def upload_wsgi_script():
    "Create and upload a wsgi script sample"
    print ">>> upload wsgi script sample"
    files.upload_template('%(project_name)s.wsgi.template' % env, '%(path)s/%(project_name)s.wsgi' % env, context=env)
    run('chmod ug+x %(path)s/%(project_name)s.wsgi' % env)

def upload_celery_conf():
    "Create and upload a Celery conf for supervisord"
    print ">>> upload celery supervisord conf"
    files.upload_template('%(project_name)s-celery.conf.template' % env, '%(path)s/%(project_name)s-celery.conf' % env, context=env)
    run('chmod ug+x %(path)s/%(project_name)s-celery.conf' % env)

def install_requirements():
    "Install the required packages from the requirements file using pip"
    print '>>> install requirements'
    require('release', provided_by=[deploy])
    run('cd %(path)s; %(pip)s install -E ve -r %(path)s/releases/%(release)s/requirements.txt' % env, pty=True)

def copy_localsettings():
    "Copy localsettings.py from root directory to release directory (if this file exists)"
    print ">>> copy localsettings"
    require('release', provided_by=[deploy])
    require('path', provided_by=[staging, production])

    with settings(warn_only=True):
        run('cp %(path)s/localsettings.py %(path)s/releases/%(release)s/%(project_name)s' % env)

def symlink_current_release():
    "Symlink our current release"
    print '>>> symlink current release'
    require('release', provided_by=[deploy])
    require('path', provided_by=[staging, production])
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous')
        run('ln -s %(release)s releases/current' % env)

def migrate():
    "Update the database"
    print '>>> migrate'
    require('project_name', provided_by=[staging, production])
    with cd('%(path)s/releases/current/%(project_name)s' % env):
        run('../../../ve/bin/python manage.py syncdb --noinput' % env, pty=True)
        if env.use_south:
            run('../../../ve/bin/python manage.py migrate' % env, pty=True)

def collectstatic():
    """Collect static files"""
    print '>>> collectstatic'
    require('project_name', provided_by=[staging, production])
    with cd('%(path)s/releases/current/%(project_name)s' % env):
        run('../../../ve/bin/python manage.py collectstatic --noinput' % env, pty=True)

def restart_gunicorn_debian():
    """Restarts gunicorn server using debian script."""
    print '>>> restart gunicorn'
    require('project_name', provided_by=[staging, production])
    with path('/sbin'):
        sudo('gunicorn-debian restart %(project_name)s' % env, shell=False)

def restart_webserver():
    """Restarts the web server."""
    if hasattr(env, 'restart_webserver'):
        env.restart_webserver()
    else:
        require('project_name', provided_by=[staging, production])
        print '>>> restart webserver'
        run('touch %(path)s/%(project_name)s.wsgi' % env)

def restart_celery():
    """Restarts the Celery task queue manager."""
    print '>>> restart Celery'
    require('project_name', provided_by=[staging, production])
    sudo('supervisorctl restart celery.%(project_name)s:' % env, shell=False)
