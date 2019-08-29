===========
Basic setup
===========

Wolne Lektury is a `Django <https://www.djangoproject.com/>`_ project.

If you're new to Django, we strongly recommend you complete
the `Django Girls Tutorial <https://tutorial.djangogirls.org/en/>`_ and/or
the official :django:`Django Tutorial <getting-started>`
to learn about setting up a Python virtual environment and general structure
of a Django project.

Getting started
---------------

Once you have your Python (version at least 3.5) installed, virtualenv created,
and the source code of Wolne Lektury checked out to a directory, then the most
basic setup is as easy as:

    $ pip install -r requirements/requirements.txt

After that, you should be able to run tests:

    $ src/manage.py test

And migrate the database and run the development server:

    $ src/manage.py migrate
    $ src/manage.py runserver


Publishing books
----------------

Books are represented as XML files.
You can download some books as source XML files and import them
into your instance either by using the admin interface,
or by running::

    src/manage.py importbooks your-directory-with-xml-files


What's next?
------------

This basic setup:

* uses a SQLite file as a database,
* has search disabled,
* does not generate PDF, EPUB or MOBI files from books,
* will generate TXT, HTML, FB2 and cover image files, but will not use a task queue.

In the next section, you'll see what additional setup is needed to solve these issues.
