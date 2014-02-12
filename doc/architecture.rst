Architecture overview
=====================

Catalogue of books
------------------

Books are kept in the :py:class:`catalogue.models.Book` model.

Books have fragments, annotated  with themes. Those are kept in the
:py:class:`catalogue.models.Fragment` model.

Both ``Books`` and ``Fragments`` can have ``Tags``, which are
:py:class:`catalogue.models.Tag` objects.

What are ``Tags`` used for?
---------------------------

Each ``Tag`` objects has a ``category`` field specyfying its meaning.
The categories are enumerated in :py:const:`catalogue.models.TAG_CATEGORIES`.

Tags are used for:

* Keeping browsable metadata. Each ``Book`` can have any number of tags
  of categories: ``author``, ``epoch``, ``kind``, ``genre``.
  Each ``Fragment`` of a book has all of those, 
  and also a number of ``theme`` tags.
* User shelves. A User can put a ``Book`` on a shelf and add some labels
  by adding a number of ``set`` tags to it. A book put on a shelf without
  any labels has a Tag with an empty name.
* Denoting :ref:`ancestor-descendant-relations` using ``book`` tags. 


.. _ancestor-descendant-relations:

Relations between ``Books``, ``Fragments`` and other ``Books``
--------------------------------------------------------------

Obviously, every ``Fragment`` comes from a particular ``Book``. This
relation is expressed with the Fragment's ``book`` field.

The source of parent-child relations between ``Books`` is
the ``dc:relation.hasPart`` metadata field, exposed by
:py:class:`librarian.dcparser.BookInfo` as ``parts``. This relation
and the order of children of one parent is expressed with the child
book's ``parent`` and ``parent_number`` fields.

But aside from that, Tags are used for managing those relationships, too.

Every ``Book`` has a matching `l-tag`. It's a ``Tag`` of category
``book`` and matching slug with an added 'l-' prefix (the prefix
is superfluous and we should remove it as some point, as it was only
needed when tag slugs had to be unique).

The `l-tag` of a ``Book`` is used on:

* all of the book's fragments,
* all of the book's descendants,
* all of the book's descendants' fragments.

This is used for:

* finding fragments of a given theme in books with a given user label,
* on a filtered book list (i.e., author's page), for eliminating
  descendants, if an ancestor is already on the list,
* when calculating tag book counts, for eliminating descendants as above,
