License
-------

  ![AGPL Logo](http://www.gnu.org/graphics/agplv3-155x51.png)
    
    Copyright © 2008,2009,2010 Fundacja Nowoczesna Polska <fundacja@nowoczesnapolska.org.pl>
    
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

 * All packages listed in requirements.txt
 * Python libraries from lib directory
 * Django applications from apps directory

How to deploy (development version)
=============

1. Checkout the source code from Github
2. Install libraries (we recommend using pip):

    pip install -r requirements.txt
    
3. Setup your local configuration based on settings.py. You need to generate a new SECRET_KEY, database stuff and domain related stuff.
4. Populate database:
    
    ./wolnelektury/manage.py syncdb
    ./wolnelektury/manage.py migrate

5. Run the server

   ./wolnelektury/manage.py runserver

    
6. Import some books which are available on http://www.wolnelektury.pl or on bitbucket mirror: http://bitbucket.org/lqc/wlbooks/
   If you use Bitbucket, you also need Mercurial to fetch books (you can install it using: pip install mercurial).
   After downloading books, log into administration, go to Books and choose 'Browse' to select book file,
   then fire 'Import book' to upload it. Some books have invalid XML, so you can get an error
   (just ignore it and look for other books).
   
7. We provide localization of the software in following languages: Polish, Russian, German, English, Spanish, French and Lithuanian.
   Translation strings are based on gettext and can be found under 'locale' dir.
   There are also JavaScript files for jQuery countdown plugin (static/js/jquery.countdown-*.js).

Full list of used open-source software
======================================

External
--------

django
--------
 - Source: [djangoproject.com](http://www.djangoproject.com/)
 - Authors: [many authors](http://code.djangoproject.com/browser/django/trunk/AUTHORS)
 - License: [BSD License](http://code.djangoproject.com/browser/django/trunk/LICENSE)
 - Type: framework

django-pagination
-----------------
 - Source: [Google Code](http://code.google.com/p/django-pagination/)
 - Authors: James Tauber <jtauber@gmail.com>, leidel@gmail.com
 - License: [New BSD License](http://www.opensource.org/licenses/bsd-license.php)
 - Type: library (django application)

django-rosetta
-----------------
 - Source: [Google Code](http://code.google.com/p/django-rosetta/)
 - Authors: James Tauber <jtauber@gmail.com>, leidel@gmail.com
 - License: [MIT License](http://www.opensource.org/licenses/mit-license.php)
 - Type: library (django application)

 
Django South
------------
- Source: [aercode.org](http://south.aeracode.org/)
- Authors: Andrew Godwin <andrew@aeracode.org>, Andy McCurdy <sedrik@gmail.com>
- License: [Apache License 2.0](http://www.opensource.org/licenses/apache2.0.php)
- Type: library (django application)

lxml
---------
 - Source: [codespeak.net](http://codespeak.net/lxml/index.html#download)
 - Authors: [many authors](http://codespeak.net/lxml/credits.html)
 - License: [BSD License](http://codespeak.net/lxml/index.html#license)
 - Type: library
 
feedparser
----------
 - Source: [Google Code](http://code.google.com/p/feedparser/)
 - Authors: Mark Pilgrim <pilgrim@gmail.com>
 - License: [MIT License](http://www.opensource.org/licenses/mit-license.php)
 - Type: library


Internal (means we hacked on sources of those): 
---------
 
django-compress
---------------
 - Source: [Google Code](http://code.google.com/p/django-compress/)
 - Authors: Andreas Pelme <andreas.pelme@gmail.com>
 - License: [MIT License](http://www.opensource.org/licenses/mit-license.php)
 - Type: library (Django application)
 
django-chunks
-------------
 - Source: [Google Code](http://code.google.com/p/django-chunks/)
 - Authors: Clint Ecker <clintecker@gmail.com>
 - License: [New BSD License](http://www.opensource.org/licenses/bsd-license.php)
 - Type: library (Django application)
 
django-newtagging
-----------------
 - Source: [BitBucket](http://www.bitbucket.org/zuber/django-newtagging/)
 - Authors: Marek Stępniowski <marek@stepniowski.com>
 - License: [MIT License](http://www.opensource.org/licenses/mit-license.php)
 - Type: library (Django aplication)
 - Notes: Aplication based on  [django-tagging](http://code.google.com/p/django-tagging/), also [MIT](http://www.opensource.org/licenses/mit-license.php) license.
 

Authors
=======
 
 * Marek Stępniowski  <marek@stepniowski.com>
 * Łukasz Rekucki <lrekucki@gmail.com>
