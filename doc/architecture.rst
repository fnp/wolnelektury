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
The categories are enumerated in :py:const:`catalogue.models.tag.TAG_CATEGORIES`.

Tags are used for:

* Keeping browsable metadata. Each ``Book`` can have any number of tags
  of categories: ``author``, ``epoch``, ``kind``, ``genre``.
  Each ``Fragment`` of a book has all of those, 
  and also a number of ``theme`` tags.
* User shelves. A User can put a ``Book`` on a shelf and add some labels
  by adding a number of ``set`` tags to it. A book put on a shelf without
  any labels has a Tag with an empty name.


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

Additionally, every ``Book`` has a many-to-many relationship `ancestor`,
onnecting it to all its ancestors, with reverse relationship called
`descendant`.  This relationship is rebuilt after a `Book` is published.
