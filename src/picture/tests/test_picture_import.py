# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from os import path
from picture.models import Picture
from catalogue.test_utils import WLTestCase


class PictureTest(WLTestCase):

    def test_import(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"))

        themes = set()
        for area in picture.areas.all():
            themes.update([
                (tag.category, tag.name)
                for tag in area.tags if tag.category in ('theme', 'thing')])
        assert themes == {('theme', 'nieporządek'), ('thing', 'Kosmos')}, \
            'Bad themes on Picture areas: %s' % themes

        pic_themes = set([tag.name for tag in picture.tags if tag.category in ('theme', 'thing')])
        assert not pic_themes, 'Unwanted themes set on Pictures: %s' % pic_themes

        picture.delete()

    def test_import_with_explicit_image(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"),
                                        path.join(path.dirname(__file__), "files/kandinsky-composition-viii.png"))

        picture.delete()

    def test_import_2(self):
        picture = Picture.from_xml_file(path.join(path.dirname(__file__), "files/kandinsky-composition-viii.xml"),
                                        path.join(path.dirname(__file__), "files/kandinsky-composition-viii.png"),
                                        overwrite=True)
        cats = set([t.category for t in picture.tags])
        assert 'epoch' in cats
        assert 'kind' in cats
