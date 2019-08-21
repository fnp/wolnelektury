=====
Setup
=====

Requirements
------------

* `Python 3.5-3.7 <http://python.org>`_
* Python requiremets: ``pip install -r requirements/requirements.txt``
* a library for your database of choice
  (see `DBs supported by Django <https://docs.djangoproject.com/en/dev/topics/install/#get-your-database-running>`_)
* `Sass <http://sass-lang.com>`_ >= 3.2 for parsing SCSS stylesheets
* Librarian has more dependencies if you want to build PDF and MOBI files, 
  see lib/librarian/README.md
* `Solr <https://lucene.apache.org/solr/>`_ server if you want to search


Running
-------
Set up the database with::

    ./manage.py migrate

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

TODO


Publishing books
----------------

Books are represented as XML files.
You can import XML files from a directory by running::

    ./manage.py importbooks ../books

Or you can publish a single XML by using publishing form in admin,
or the publishing API.
