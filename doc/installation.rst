=====
Setup
=====

Requirements
------------

* `Python 2.7 <http://python.org>`_
* Python requiremets: ``pip install -r requirements.txt``
* a library for your database of choice
  (see `DBs supported by Django <http://docs.djangoproject.com/en/dev/topics/install/#get-your-database-running>`_)
* `Sass <http://sass-lang.com>`_ >= 3.2 for parsing SCSS stylesheets
* Librarian (bundled as a git submodule, remember to ``git submodule update --init``
* Librarian has more dependencies if you want to build PDF and MOBI files, 
  see lib/librarian/README.md
* `Solr <https://lucene.apache.org/solr/>`_ server if you want to search


Running
-------
Set up the database with::

    ./manage.py syncdb --migrate

Run the dev server with::

    ./manage.py runserver

Some tasks (like generating e-books) run in a seperate
Celery process by default, so you'll also need to run::

    celery -A wolnelektury worker --loglevel=INFO

Or, if you don't want to run a separate Celery daemon, set this
in your ``localsettings.py``::

    CELERY_ALWAYS_EAGER = True


Deployment
----------
Setup your server in fabfile.py and do::

    fab <your_server_name> deploy

Initial deploy will stop and ask you to provide a localsettings.py file.
A sample localsettings.py will be put on your server, as well as
sample configuration for `Nginx <http://nginx.org/>`_,
`Gunicorn <http://gunicorn.org/>`_ and
`Supervisord <http://supervisord.org/>`_.


Publishing books
----------------

Books are represented as XML files.
You can import XML files from a directory by running::

    ./manage.py importbooks ../books

Or you can publish a single XML by using publishing form in admin,
or the publishing API.
