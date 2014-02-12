# -*- coding: utf-8 -*-
# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.core.files.base import ContentFile
from django.test import Client
from catalogue import models
from catalogue.test_utils import *


class BooksByTagTests(WLTestCase):
    """ tests the /katalog/category/tag page for found books """

    def setUp(self):
        WLTestCase.setUp(self)
        author = PersonStub(("Common",), "Man")

        # grandchild
        self.gchild_info = BookInfoStub(genre='Genre', epoch='Epoch', kind='Kind', author=author,
                                        **info_args("GChild"))
        # child
        self.child_info = BookInfoStub(genre='Genre', epoch='Epoch', kind='Other Kind', author=author,
                                       parts=[self.gchild_info.url],
                                       **info_args("Child"))
        # parent
        self.parent_info = BookInfoStub(genre='Genre', epoch='Epoch', kind='Kind', author=author,
                                        parts=[self.child_info.url],
                                        **info_args("Parent"))

        self.book_file = ContentFile('<utwor />')

    def test_nonexistent_tag(self):
        """ Looking for a non-existent tag should yield 404 """
        # NOTE: this yields a false positive, 'cause of URL change
        self.assertEqual(404, self.client.get('/katalog/autor/czeslaw_milosz/').status_code)

    def test_book_tag(self):
        """ Looking for a book tag isn't permitted """
        models.Book.from_text_and_meta(self.book_file, self.gchild_info)
        self.assertEqual(404, self.client.get('/katalog/gchild/').status_code)

    def test_tag_empty(self):
        """ Tag with no books should return no books """
        models.Book.from_text_and_meta(self.book_file, self.gchild_info)
        models.Tag.objects.create(name='Empty tag', slug='empty', category='author')

        context = self.client.get('/katalog/autor/empty/').context
        self.assertEqual(0, len(context['object_list']))

    def test_tag_eliminate(self):
        """ Filtering by tag should only yield top-level qualifying books. """
        for info in self.gchild_info, self.child_info, self.parent_info:
            models.Book.from_text_and_meta(self.book_file, info)

        # all three qualify
        context = self.client.get('/katalog/gatunek/genre/').context
        self.assertEqual([book.title for book in context['object_list']],
                         ['Parent'])

        # parent and gchild qualify, child doesn't
        context = self.client.get('/katalog/rodzaj/kind/').context
        self.assertEqual([book.title for book in context['object_list']],
                         ['Parent'])

        # Filtering by child's tag should yield the child
        context = self.client.get('/katalog/rodzaj/other-kind/').context
        self.assertEqual([book.title for book in context['object_list']],
                         ['Child'])


class TagRelatedTagsTests(WLTestCase):
    """ tests the /katalog/category/tag/ page for related tags """

    def setUp(self):
        WLTestCase.setUp(self)
        self.client = Client()
        author = PersonStub(("Common",), "Man")

        gchild_info = BookInfoStub(author=author, genre="GchildGenre", epoch='Epoch', kind="Kind",
                                   **info_args(u"GChild"))
        child1_info = BookInfoStub(author=author, genre="ChildGenre", epoch='Epoch', kind="ChildKind",
                                   parts=[gchild_info.url],
                                   **info_args(u"Child1"))
        child2_info = BookInfoStub(author=author, genre="ChildGenre", epoch='Epoch', kind="ChildKind",
                                   **info_args(u"Child2"))
        parent_info = BookInfoStub(author=author, genre="Genre", epoch='Epoch', kind="Kind",
                                   parts=[child1_info.url, child2_info.url],
                                   **info_args(u"Parent"))

        for info in gchild_info, child1_info, child2_info, parent_info:
            book_text = """<utwor><opowiadanie><akap>
                <begin id="m01" />
                    <motyw id="m01">Theme, %sTheme</motyw>
                    Ala ma kota
                <end id="m01" />
                </akap></opowiadanie></utwor>
                """ % info.title.encode('utf-8')
            book = models.Book.from_text_and_meta(ContentFile(book_text), info)
            book.save()

        tag_empty = models.Tag(name='Empty tag', slug='empty', category='author')
        tag_empty.save()

    def test_empty(self):
        """ empty tag should have no related tags """

        cats = self.client.get('/katalog/autor/empty/').context['categories']
        self.assertEqual(cats, {}, 'tags related to empty tag')

    def test_has_related(self):
        """ related own and descendants' tags should be generated """

        cats = self.client.get('/katalog/rodzaj/kind/').context['categories']
        self.assertTrue('Common Man' in [tag.name for tag in cats['author']],
                        'missing `author` related tag')
        self.assertTrue('Epoch' in [tag.name for tag in cats['epoch']],
                        'missing `epoch` related tag')
        self.assertTrue("ChildKind" in [tag.name for tag in cats['kind']],
                        "missing `kind` related tag")
        self.assertTrue("Genre" in [tag.name for tag in cats['genre']],
                        'missing `genre` related tag')
        self.assertTrue("ChildGenre" in [tag.name for tag in cats['genre']],
                        "missing child's related tag")
        self.assertTrue("GchildGenre" in [tag.name for tag in cats['genre']],
                        "missing grandchild's related tag")
        self.assertTrue('Theme' in [tag.name for tag in cats['theme']],
                        "missing related theme")
        self.assertTrue('Child1Theme' in [tag.name for tag in cats['theme']],
                        "missing child's related theme")
        self.assertTrue('GChildTheme' in [tag.name for tag in cats['theme']],
                        "missing grandchild's related theme")


    def test_related_differ(self):
        """ related tags shouldn't include filtering tags """

        response = self.client.get('/katalog/rodzaj/kind/')
        cats = response.context['categories']
        self.assertFalse('Kind' in [tag.name for tag in cats['kind']],
                         'filtering tag wrongly included in related')
        cats = self.client.get('/katalog/motyw/theme/').context['categories']
        self.assertFalse('Theme' in [tag.name for tag in cats['theme']],
                         'filtering theme wrongly included in related')

    def test_parent_tag_once(self):
        """ if parent and descendants have a common tag, count it only once """

        cats = self.client.get('/katalog/rodzaj/kind/').context['categories']
        self.assertEqual([(tag.name, tag.count) for tag in cats['epoch']],
                         [('Epoch', 1)],
                         'wrong related tag epoch tag on tag page')


    def test_siblings_tags_count(self):
        """ if children have tags and parent hasn't, count the children """

        cats = self.client.get('/katalog/epoka/epoch/').context['categories']
        self.assertTrue(('ChildKind', 2) in [(tag.name, tag.count) for tag in cats['kind']],
                    'wrong related kind tags on tag page')

        # all occurencies of theme should be counted
        self.assertTrue(('Theme', 4) in [(tag.name, tag.count) for tag in cats['theme']],
                    'wrong related theme count')


class CleanTagRelationTests(WLTestCase):
    """ tests for tag relations cleaning after deleting things """

    def setUp(self):
        WLTestCase.setUp(self)
        author = PersonStub(("Common",), "Man")

        book_info = BookInfoStub(author=author, genre="G", epoch='E', kind="K",
                                   **info_args(u"Book"))
        book_text = """<utwor><opowiadanie><akap>
            <begin id="m01" /><motyw id="m01">Theme</motyw>Ala ma kota
            <end id="m01" />
            </akap></opowiadanie></utwor>
            """
        self.book = models.Book.from_text_and_meta(ContentFile(book_text), book_info)

    def test_delete_objects(self):
        """ there should be no related tags left after deleting some objects """

        models.Book.objects.all().delete()
        cats = self.client.get('/katalog/rodzaj/k/').context['categories']
        self.assertEqual(cats, {})
        self.assertEqual(models.Fragment.objects.all().count(), 0,
                         "orphaned fragments left")
        self.assertEqual(models.Tag.intermediary_table_model.objects.all().count(), 0,
                         "orphaned TagRelation objects left")

    def test_deleted_tag(self):
        """ there should be no tag relations left after deleting tags """

        models.Tag.objects.all().delete()
        self.assertEqual(len(self.book.related_info()['tags']), 0)
        self.assertEqual(len(self.book.related_themes()), 0)
        self.assertEqual(models.Tag.intermediary_table_model.objects.all().count(), 0,
                         "orphaned TagRelation objects left")


class TestIdenticalTag(WLTestCase):

    def setUp(self):
        WLTestCase.setUp(self)
        author = PersonStub((), "Tag")

        self.book_info = BookInfoStub(author=author,
                                 genre="tag",
                                 epoch='tag',
                                 kind="tag",
                                   **info_args(u"tag"))
        self.book_text = """<utwor>
            <opowiadanie>
            <akap>
                <begin id="m01" /><motyw id="m01">tag</motyw>Ala ma kota<end id="m01" />
            </akap>
            </opowiadanie>
            </utwor>
        """


    def test_book_tags(self):
        """ there should be all related tags in relevant categories """
        book = models.Book.from_text_and_meta(ContentFile(self.book_text), self.book_info)

        related_info = book.related_info()
        related_themes = book.related_themes()
        for category in 'author', 'kind', 'genre', 'epoch':
            self.assertTrue('tag' in [tag['slug'] for tag in related_info['tags'][category]],
                            'missing related tag for %s' % category)
        self.assertTrue('tag' in [tag.slug for tag in related_themes])

    def test_qualified_url(self):
        models.Book.from_text_and_meta(ContentFile(self.book_text), self.book_info)
        categories = {'author': 'autor', 'theme': 'motyw', 'epoch': 'epoka', 'kind':'rodzaj', 'genre':'gatunek'}
        for cat, localcat in categories.iteritems():
            context = self.client.get('/katalog/%s/tag/' % localcat).context
            self.assertEqual(1, len(context['object_list']))
            self.assertNotEqual({}, context['categories'])
            self.assertFalse(cat in context['categories'])


class BookTagsTests(WLTestCase):
    """ tests the /katalog/lektura/book/ page for related tags """

    def setUp(self):
        WLTestCase.setUp(self)
        author1 = PersonStub(("Common",), "Man")
        author2 = PersonStub(("Jim",), "Lazy")

        child_info = BookInfoStub(authors=(author1, author2), genre="ChildGenre", epoch='Epoch', kind="ChildKind",
                                   **info_args(u"Child"))
        parent_info = BookInfoStub(author=author1, genre="Genre", epoch='Epoch', kind="Kind",
                                   parts=[child_info.url],
                                   **info_args(u"Parent"))

        for info in child_info, parent_info:
            book_text = """<utwor><opowiadanie><akap>
                <begin id="m01" />
                    <motyw id="m01">Theme, %sTheme</motyw>
                    Ala ma kota
                <end id="m01" />
                </akap></opowiadanie></utwor>
                """ % info.title.encode('utf-8')
            models.Book.from_text_and_meta(ContentFile(book_text), info)

    def test_book_tags(self):
        """ book should have own tags and whole tree's themes """

        book = models.Book.objects.get(slug='parent')
        related_info = book.related_info()
        related_themes = book.related_themes()

        self.assertEqual([t['slug'] for t in related_info['tags']['author']],
                         ['common-man'])
        self.assertEqual([t['slug'] for t in related_info['tags']['kind']],
                         ['kind'])
        self.assertEqual([(tag.name, tag.count) for tag in related_themes],
                         [('ChildTheme', 1), ('ParentTheme', 1), ('Theme', 2)])

    def test_catalogue_tags(self):
        """ test main page tags and counts """
        context = self.client.get('/katalog/').context
        self.assertEqual([(tag.name, tag.book_count) for tag in context['categories']['author']],
                         [('Jim Lazy', 1), ('Common Man', 1)])
        self.assertEqual([(tag.name, tag.book_count) for tag in context['categories']['theme']],
                         [('ChildTheme', 1), ('ParentTheme', 1), ('Theme', 2)])

