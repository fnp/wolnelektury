License
-------

  ![AGPL Logo](http://www.gnu.org/graphics/agplv3-155x51.png)
    
    Copyright © 2008-2019 Fundacja Nowoczesna Polska <fundacja@nowoczesnapolska.org.pl>
    
    For full list of contributors see AUTHORS section at the end. 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
Dependencies
============

 * Python 3.4+
 * All packages listed in requirements.txt
 * Sass>=3.2

How to deploy (development version)
=============

1. Checkout the source code from Git and enter the directory
2. Install libraries (we recommend using pip):

    pip install -r requirements/requirements.txt

3. Setup your local configuration in src/wolnelektury/localsettings.py. You need to generate a new SECRET_KEY, database stuff and domain related stuff.
4. Populate database:
    
    ./manage.py migrate

5. Run the server

   ./manage.py runserver

    
6. Import some books which are available on http://www.wolnelektury.pl or on bitbucket mirror: http://bitbucket.org/lqc/wlbooks/
   If you use Bitbucket, you also need Mercurial to fetch books (you can install it using: pip install mercurial).
   After downloading books, log into administration, go to Books and choose 'Browse' to select book file,
   then fire 'Import book' to upload it. Some books have invalid XML, so you can get an error
   (just ignore it and look for other books).
   
7. We provide localization of the software in following languages: Polish, Russian, German, English, Spanish, French and Lithuanian.
   Translation strings are based on gettext and can be found under 'locale' dir.
   There are also JavaScript files for jQuery countdown plugin (static/js/jquery.countdown-*.js).

Bundled software
================

* django-chunks
  in `src/chunks`
  based on [django-chunks](http://code.google.com/p/django-chunks/)
  by Clint Ecker <clintecker@gmail.com>,
  [New BSD License](http://www.opensource.org/licenses/bsd-license.php)
* [django-newtagging](http://www.bitbucket.org/zuber/django-newtagging/)
  in `src/newtagging`
  by Marek Stępniowski <marek@stepniowski.com>,
  [MIT License](http://www.opensource.org/licenses/mit-license.php),
  based on [django-tagging](http://code.google.com/p/django-tagging/), also under [MIT License](http://www.opensource.org/licenses/mit-license.php)
* [jPlayer](http://jplayer.org/)
  in `src/catalogue/static/jplayer`
  by Happyworm,
  [MIT License](http://opensource.org/licenses/MIT)
* [Switch template tag](http://djangosnippets.org/snippets/967/)
  in `src/wolnelektury/templatetags/switch_tag.py`
  by adurdin
* Javascript in `src/wolnelektury/static/js/contrib`
  with relevant attribution and licensing
  


Authors
=======
 * Marek Stępniowski  <marek@stepniowski.com>
 * Łukasz Rekucki <lrekucki@gmail.com>
 * Radek Czajka
 * Łukasz Anwajler
 * Marcin Koziej
 * Aleksander Łukasz
 * Jan Szejko
 * Mariusz Machuta
