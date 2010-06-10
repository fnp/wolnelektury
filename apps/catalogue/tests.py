# -*- coding: utf-8 -*-
from django.test import TestCase
from catalogue import models, views
from django.core.files.base import ContentFile
from django.contrib.auth.models import User, AnonymousUser
from django.test.client import Client

from nose.tools import raises
from StringIO import StringIO

class BasicSearchLogicTests(TestCase):

    def setUp(self):
        self.author_tag = models.Tag.objects.create(
                                name=u'Adam Mickiewicz [SubWord]',
                                category=u'author', slug="one")

        self.unicode_tag = models.Tag.objects.create(
                                name=u'Tadeusz Żeleński (Boy)',
                                category=u'author', slug="two")

        self.polish_tag = models.Tag.objects.create(
                                name=u'ĘÓĄŚŁŻŹĆŃęóąśłżźćń',
                                category=u'author', slug="three")

    @raises(ValueError)
    def test_empty_query(self):
        """ Check that empty queries raise an error. """
        views.find_best_matches(u'')

    @raises(ValueError)
    def test_one_letter_query(self):
        """ Check that one letter queries aren't permitted. """
        views.find_best_matches(u't')

    def test_match_by_prefix(self):
        """ Tags should be matched by prefix of words within it's name. """
        self.assertEqual(views.find_best_matches(u'Ada'), (self.author_tag,))
        self.assertEqual(views.find_best_matches(u'Mic'), (self.author_tag,))
        self.assertEqual(views.find_best_matches(u'Mickiewicz'), (self.author_tag,))

    def test_match_case_insensitive(self):
        """ Tag names should match case insensitive. """
        self.assertEqual(views.find_best_matches(u'adam mickiewicz'), (self.author_tag,))

    def test_match_case_insensitive_unicode(self):
        """ Tag names should match case insensitive (unicode). """
        self.assertEqual(views.find_best_matches(u'tadeusz żeleński (boy)'), (self.unicode_tag,))

    def test_word_boundary(self):
        self.assertEqual(views.find_best_matches(u'SubWord'), (self.author_tag,))
        self.assertEqual(views.find_best_matches(u'[SubWord'), (self.author_tag,))

    def test_unrelated_search(self):
        self.assertEqual(views.find_best_matches(u'alamakota'), tuple())
        self.assertEqual(views.find_best_matches(u'Adama'), ())

    def test_infix_doesnt_match(self):
        """ Searching for middle of a word shouldn't match. """
        self.assertEqual(views.find_best_matches(u'deusz'), tuple())

    def test_diactricts_removal_pl(self):
        """ Tags should match both with and without national characters. """
        self.assertEqual(views.find_best_matches(u'ĘÓĄŚŁŻŹĆŃęóąśłżźćń'), (self.polish_tag,))
        self.assertEqual(views.find_best_matches(u'EOASLZZCNeoaslzzcn'), (self.polish_tag,))
        self.assertEqual(views.find_best_matches(u'eoaslzzcneoaslzzcn'), (self.polish_tag,))

    def test_diactricts_query_removal_pl(self):
        """ Tags without national characters shouldn't be matched by queries with them. """
        self.assertEqual(views.find_best_matches(u'Adąm'), ())

    def test_sloppy(self):
        self.assertEqual(views.find_best_matches(u'Żelenski'), (self.unicode_tag,))
        self.assertEqual(views.find_best_matches(u'zelenski'), (self.unicode_tag,))


class PersonStub(object):

    def __init__(self, first_names, last_name):
        self.first_names = first_names
        self.last_name = last_name

from slughifi import slughifi

class BookInfoStub(object):

    def __init__(self, **kwargs):            
        self.__dict = kwargs

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self.__dict[key] = value
        return object.__setattr__(self, key, value)

    def __getattr__(self, key):
        return self.__dict[key]

    def to_dict(self):
        return dict((key, unicode(value)) for key, value in self.__dict.items())

def info_args(title):
    """ generate some keywords for comfortable BookInfoCreation  """
    slug = unicode(slughifi(title))
    return {'title': unicode(title),
            'slug': slug,
            'url': u"http://wolnelektury.pl/example/%s" % slug,
            'about': u"http://wolnelektury.pl/example/URI/%s" % slug,
            }

class BookImportLogicTests(TestCase):

    def setUp(self):
        self.book_info = BookInfoStub(
            url=u"http://wolnelektury.pl/example/default_book",
            about=u"http://wolnelektury.pl/example/URI/default_book",
            title=u"Default Book",
            author=PersonStub(("Jim",), "Lazy"),
            kind="X-Kind",
            genre="X-Genre",
            epoch="X-Epoch",
        )

        self.expected_tags = [
           ('author', 'jim-lazy'),
           ('genre', 'x-genre'),
           ('epoch', 'x-epoch'),
           ('kind', 'x-kind'),
        ]
        self.expected_tags.sort()

    def tearDown(self):
        for book in models.Book.objects.all():
            if book.xml_file:
                book.xml_file.delete()
            if book.html_file:
                book.html_file.delete()

    def test_empty_book(self):
        BOOK_TEXT = "<utwor />"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        self.assertEqual(book.title, "Default Book")
        self.assertEqual(book.slug, "default_book")
        self.assert_(book.parent is None)
        self.assertFalse(book.has_html_file())

        # no fragments generated
        self.assertEqual(book.fragments.count(), 0)

        # TODO: this should be filled out probably...
        self.assertEqual(book.wiki_link, '')
        self.assertEqual(book.gazeta_link, '')
        self.assertEqual(book._short_html, '')
        self.assertEqual(book.description, '')

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)
    
    def test_not_quite_empty_book(self):
        """ Not empty, but without any real text.
        
        Should work like any other non-empty book.
        """
        
        BOOK_TEXT = """<utwor>
        <liryka_l>
            <nazwa_utworu>Nic</nazwa_utworu>
        </liryka_l></utwor>
        """
        
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assertTrue(book.has_html_file())

    def test_book_with_fragment(self):
        BOOK_TEXT = """<utwor>
        <opowiadanie>
            <akap><begin id="m01" /><motyw id="m01">Love</motyw>Ala ma kota<end id="m01" /></akap>
        </opowiadanie></utwor>
        """

        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)
        self.assertTrue(book.has_html_file())

        self.assertEqual(book.fragments.count(), 1)
        self.assertEqual(book.fragments.all()[0].text, u'<p class="paragraph">Ala ma kota</p>\n')

        self.assert_(('theme', 'love') in [ (tag.category, tag.slug) for tag in book.tags ])

    def test_book_replace_title(self):
        BOOK_TEXT = """<utwor />"""
        self.book_info.title = u"Extraordinary"
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.assertEqual(tags, self.expected_tags)

    def test_book_replace_author(self):
        BOOK_TEXT = """<utwor />"""
        self.book_info.author = PersonStub(("Hans", "Christian"), "Andersen")
        book = models.Book.from_text_and_meta(ContentFile(BOOK_TEXT), self.book_info)

        tags = [ (tag.category, tag.slug) for tag in book.tags ]
        tags.sort()

        self.expected_tags.remove(('author', 'jim-lazy'))
        self.expected_tags.append(('author', 'hans-christian-andersen'))
        self.expected_tags.sort()

        self.assertEqual(tags, self.expected_tags)

        # the old tag should disappear 
        self.assertRaises(models.Tag.DoesNotExist, models.Tag.objects.get,
                    slug="jim-lazy", category="author")


    
class BooksByTagTests(TestCase):
    """ tests the /katalog/tag page for found books """
    
    def setUp(self):
        author = PersonStub(("Common",), "Man")
        tags = dict(genre='G', epoch='E', author=author, kind="K")

        # grandchild
        kwargs = info_args(u"GChild")
        kwargs.update(tags)
        gchild_info = BookInfoStub(**kwargs)
        # child
        kwargs = info_args(u"Child")
        kwargs.update(tags)
        child_info = BookInfoStub(parts=[gchild_info.url], **kwargs)
        # other grandchild
        kwargs = info_args(u"Different GChild")
        kwargs.update(tags)
        diffgchild_info = BookInfoStub(**kwargs)
        # other child
        kwargs = info_args(u"Different Child")
        kwargs.update(tags)
        kwargs['kind'] = 'K2'
        diffchild_info = BookInfoStub(parts=[diffgchild_info.url], **kwargs)
        # parent
        kwargs = info_args(u"Parent")
        kwargs.update(tags)
        parent_info = BookInfoStub(parts=[child_info.url, diffchild_info.url], **kwargs)

        # create the books
        book_file = ContentFile('<utwor />')
        for info in gchild_info, child_info, diffgchild_info, diffchild_info, parent_info:
            book = models.Book.from_text_and_meta(book_file, info)

        # useful tags
        self.author = models.Tag.objects.get(name='Common Man', category='author')
        tag_empty = models.Tag(name='Empty tag', slug='empty', category='author')
        tag_empty.save()
        
        self.client = Client()
    
    
    def tearDown(self):
        for book in models.Book.objects.all():
            if book.xml_file:
                book.xml_file.delete()
            if book.html_file:
                book.html_file.delete()

    
    def test_nonexistent_tag(self):
        """ Looking for a non-existent tag should yield 404 """
        self.assertEqual(404, self.client.get('/katalog/czeslaw_milosz/').status_code)
        
    def test_book_tag(self):
        """ Looking for a book tag isn't permitted """
        self.assertEqual(404, self.client.get('/katalog/parent/').status_code)
    
    def test_tag_empty(self):
        """ Tag with no books should return no books """
        context = self.client.get('/katalog/empty/').context
        self.assertEqual(0, len(context['object_list']))
    
    def test_tag_common(self):
        """ Filtering by tag should only yield top-level books. """
        context = self.client.get('/katalog/%s/' % self.author.slug).context
        self.assertEqual([book.title for book in context['object_list']],
                         ['Parent'])

    def test_tag_child(self):
        """ Filtering by child's tag should yield the child """
        context = self.client.get('/katalog/k2/').context
        self.assertEqual([book.title for book in context['object_list']],
                         ['Different Child'])

    def test_tag_child_jump(self):
        """ Of parent and grandchild, only parent should be returned. """
        context = self.client.get('/katalog/k/').context
        self.assertEqual([book.title for book in context['object_list']],
                         ['Parent'])
        

class TagRelatedTagsTests(TestCase):
    """ tests the /katalog/tag/ page for related tags """
    
    def setUp(self):
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
                    Ala ma kąta
                <end id="m01" />
                </akap></opowiadanie></utwor>
                """ % info.title.encode('utf-8')
            book = models.Book.from_text_and_meta(ContentFile(book_text), info)
            book.save()
        
        tag_empty = models.Tag(name='Empty tag', slug='empty', category='author')
        tag_empty.save()

        self.client = Client()
    
    
    def tearDown(self):
        for book in models.Book.objects.all():
            if book.xml_file:
                book.xml_file.delete()
            if book.html_file:
                book.html_file.delete()
    
    
    def test_empty(self):
        """ empty tag should have no related tags """
        
        cats = self.client.get('/katalog/empty/').context['categories']
        self.assertEqual(cats, {}, 'tags related to empty tag')
    
    
    def test_has_related(self):
        """ related own and descendants' tags should be generated """
        
        cats = self.client.get('/katalog/kind/').context['categories']
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
        
        cats = self.client.get('/katalog/kind/').context['categories']
        self.assertFalse('Kind' in [tag.name for tag in cats['kind']],
                         'filtering tag wrongly included in related')
        cats = self.client.get('/katalog/theme/').context['categories']
        self.assertFalse('Theme' in [tag.name for tag in cats['theme']],
                         'filtering theme wrongly included in related')
    
    
    def test_parent_tag_once(self):
        """ if parent and descendants have a common tag, count it only once """

        cats = self.client.get('/katalog/kind/').context['categories']
        self.assertEqual([(tag.name, tag.count) for tag in cats['epoch']],
                         [('Epoch', 1)],
                         'wrong related tag epoch tag on tag page')
    
    
    def test_siblings_tags_add(self):
        """ if children have tags and parent hasn't, count the children """
        
        cats = self.client.get('/katalog/epoch/').context['categories']
        self.assertTrue(('ChildKind', 2) in [(tag.name, tag.count) for tag in cats['kind']],
                    'wrong related kind tags on tag page')
    
    def test_themes_add(self):
        """ all occurencies of theme should be counted """

        cats = self.client.get('/katalog/epoch/').context['categories']
        self.assertTrue(('Theme', 4) in [(tag.name, tag.count) for tag in cats['theme']],
                    'wrong related theme count')
        
        
    

