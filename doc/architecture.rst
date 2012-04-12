Architecture overview
=====================

Books
-----

Books are kept in the :py:class:`catalogue.models.Book` model.  Dublin Core
metadata, read by :py:mod:`librarian.dcparser.BookInfo`, are put in the
`extra_info` JSON field.

Authors, kinds, epochs, genres are kept in :py:class:`catalogue.models.Tag`
model with `category` field set to appriopriate value.

:py:class:`catalogue.models.Tag` also contains :ref:`user-shelves`
and :ref:`parent-relations`.


User shelves
------------

User shelves (or tags on user's shelf) are just :py:class:`catalogue.models.Tag`
objects with ``category='set'`` and ``user`` set to the owner. Shelves' slugs
are generated automatically using :py:fun:`catalogue.utils.get_random_hash`.


Parent relations
----------------

The source of parent relations is the
:py:class:`librarian.dcparser.BookInfo.parts` metadata.

Parent relations are kept primarily in the :py:attribute:`catalogue.models.Book.parent`
and :py:attribute:`catalogue.models.Book.parent_number` fields.

They're also cached as :py:class:`Tag <catalogue.models.Tag>` relations.
Each book has its tag (with :py:attribute:`slug <catalogue.models.Book.slug>`
starting with ``l-``).  All of book's descendants (NOT the book
itself) have its tag attached.

Arguably, this scheme has some potential for inconsistency.
