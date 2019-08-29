==============
Advanced setup
==============

Changing database backend
-------------------------

The project does not rely on any features specific to a database backend, so you can choose
any of the :django:`backends supported by Django <topics/install/#get-your-database-running>`.


Search engine
-------------

.. todo::

   Setting up Solr to be documented.
    

Task queue
----------

Some tasks (like generating e-books) run in a seperate
Celery process by default, so you'll also need to run::

    celery -A wolnelektury worker --loglevel=INFO



Generating PDF files
--------------------

.. todo::

   To be documented.


Generating EPUB files
---------------------

.. todo::

   To be documented.


Generating MOBI files
---------------------

.. todo::

   To be documented.
