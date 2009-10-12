from __future__ import with_statement # needed for python 2.5
from fabric.api import *

import os

# Globals
env.project_name = 'wolnelektury'


# ===========
# = Servers =
# ===========
def staging():
    """Use staging server"""
    env.hosts = ['zuber@stigma.nowoczesnapolska.org.pl:2222']
    env.path = '/var/lektury'
    env.python = '/usr/bin/python'
    env.virtualenv = '/usr/bin/virtualenv'
    env.pip = '/usr/bin/pip'
    
def production():
    """Use production server"""
    env.hosts = ['fundacja@wolnelektury.pl:22123']
    env.path = '/opt/lektury'
    env.python = '/opt/lektury/basevirtualenv/bin/python'
    env.virtualenv = '/opt/lektury/basevirtualenv/bin/virtualenv'
    env.pip = '/opt/lektury/basevirtualenv/bin/pip'

# =========
# = Tasks =
# =========
def test():
    "Run the test suite and bail out if it fails"
    require('hosts', 'path', provided_by=[staging, production])
    result = run('cd %(path)s/%(project_name)s; %(python)s manage.py test' % env)

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
    upload_requirements_bundle()
    install_requirements()
    symlink_current_release()
    migrate()
    restart_webserver()

def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', 'path', provided_by=[localhost,webserver])
    env.version = version
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;', pty=True)
        run('ln -s %(version)s releases/current' % env, pty=True)
    restart_webserver()

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
    
# def setup():
#     """
#     Setup a fresh virtualenv as well as a few useful directories, then run
#     a full deployment
#     """
#     require('hosts', provided_by=[staging, production])
#     require('path')
#     sudo('aptitude install -y python-setuptools')
#     sudo('easy_install pip')
#     sudo('pip install virtualenv')
#     sudo('aptitude install -y apache2-threaded')
#     sudo('aptitude install -y libapache2-mod-wsgi') # beware, outdated on hardy!
#     # we want to get rid of the default apache config
#     sudo('cd /etc/apache2/sites-available/; a2dissite default;', pty=True)
#     sudo('mkdir -p %(path)s; chown %(user)s:%(user)s %(path)s;' % env, pty=True)
#     run('ln -s %(path)s www;' % env, pty=True) # symlink web dir in home
#     with cd(env.path):
#         run('virtualenv .;' % env, pty=True)
#         run('mkdir logs; chmod a+w logs; mkdir releases; mkdir shared; mkdir packages;' % env, pty=True)
#         if env.use_photologue: run('mkdir photologue');
#         run('cd releases; ln -s . current; ln -s . previous;', pty=True)
#     deploy()


# =====================================================================
# = Helpers. These are called by other functions rather than directly =
# =====================================================================
def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it"
    print '>>> upload tar from git'
    require('release', provided_by=[deploy])
    local('git archive --format=tar master | gzip > %(release)s.tar.gz' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env, pty=True)
    run('mkdir -p %(path)s/packages' % env, pty=True)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env, pty=True)
    local('rm %(release)s.tar.gz' % env)

def upload_requirements_bundle():
    "Create a pybundle from requirements.txt file and upload it"
    print '>>> upload requirements bundle'
    require('release', provided_by=[deploy])
    requirements_mtime = os.path.getmtime('requirements.txt')
    pybundle_mtime = 0
    try:
        pybundle_mtime = os.path.getmtime('requirements.pybundle')
    except os.error:
        pass
    if pybundle_mtime < requirements_mtime:
        pip_options = file('pip-options.txt').read().strip()
        local('pip bundle %s -r requirements.txt requirements.pybundle' % pip_options)
    put('requirements.pybundle', '%(path)s/releases/%(release)s' % env)

def install_requirements():
    "Install the required packages from the requirements file using pip"
    print '>>> install requirements'
    require('release', provided_by=[deploy])
    with cd('%(path)s/releases/%(release)s' % env):
        run('%(virtualenv)s --no-site-packages .' % env)
        run('%(pip)s install -E . requirements.pybundle' % env)

def symlink_current_release():
    "Symlink our current release"
    print '>>> symlink current release'
    require('release', provided_by=[deploy])
    require('path', provided_by=[staging, production])
    with cd(env.path):
        with settings(
            hide('warnings', 'running', 'stdout', 'stderr'),
            warn_only=True
        ):
            run('rm releases/previous; mv releases/current releases/previous;')
        
        run('ln -s %(release)s releases/current' % env)

def migrate():
    "Update the database"
    print '>>> migrate'
    require('project_name', provided_by=[staging, production])
    with cd('%(path)s/releases/current/%(project_name)s' % env):
        run('../bin/python manage.py syncdb --noinput' % env, pty=True)
        run('../bin/python manage.py migrate' % env, pty=True)

def restart_webserver():
    "Restart the web server"
    print '>>> restart webserver'
    run('touch %(path)s/releases/current/%(project_name)s/%(project_name)s.wsgi' % env)

# def install_site():
#     "Add the virtualhost file to apache"
#     require('release', provided_by=[deploy, setup])
#     #sudo('cd %(path)s/releases/%(release)s; cp %(project_name)s%(virtualhost_path)s%(project_name)s /etc/apache2/sites-available/' % env)
#     sudo('cd %(path)s/releases/%(release)s; cp vhost.conf /etc/apache2/sites-available/%(project_name)s' % env)
#     sudo('cd /etc/apache2/sites-available/; a2ensite %(project_name)s' % env, pty=True) 
