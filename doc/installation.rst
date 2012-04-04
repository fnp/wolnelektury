=====
Setup
=====

Requirements
------------

* `Python 2.6+ <http://python.org>`_
* Everyting from the ``requirements.txt`` file
* a library for your database of choice
 (see `DBs supported by Django <http://docs.djangoproject.com/en/dev/topics/install/#get-your-database-running>`_)
* `puLucene <https://github.com/fnp/pylucene/>`_ for search
* Librarian dependencies, see lib/librarian/README.md


Installation
------------
Installing database::

    cd wolnelektury
    ./manage.py syncdb
    ./manage.py migrate


Running
-------

You can run the server with::

    ./manage.py runserver

If you want to run lengthy tasks (like generating e-book files) in a seperate
Celery process (this is the default), you'll also need to run:

    ./manage.py celeryd --loglevel=INFO

If you don't want to run a separate Celery daemon, make sure you set this
option in your ``localsettings.py``::

    CELERY_ALWAYS_EAGER = True


Deployment
----------
Setup your server in fabfile.py and do::

    fab <your_server_name> setup

Aside from uploading a current (git's HEAD) version of the app this will also
download all dependencies into a `virtualenv <http://www.virtualenv.org>`_, 
create a VHost and WSGI files for running with Apache and mod_wsgi, and
a celery config file for `supervisord <http://supervisord.org/>`_.

To deploy a new version into an existing setup, do:

    fab <your_server_name> deploy

This will also check for new dependencied, migrate your app and restart the
WSGI server and Celery under supervisord.
