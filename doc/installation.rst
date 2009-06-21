==========
Instalacja
==========

Wymagania
---------
Do działania serwisu wymagane są:

* `Python 2.5 <http://python.org>`_
* `Django 1.0 <http://djangoproject.com>`_
* `lxml 2.2 <http://codespeak.net/lxml/>`_

Jeżeli używasz Pythona 2.4 lub chcesz użyć bazy danych innej niż SQLite, wymagana jest jeszcze:

* biblioteka do obsługi wybranej bazy danych (`biblioteki wspierane przez Django <http://docs.djangoproject.com/en/dev/topics/install/#get-your-database-running>`_)

Do pracy nad dokumentacją, którą teraz czytasz, potrzebne są:

* `Sphinx 0.6.2 <http://sphinx.pocoo.org/>`_ i zależności

Wyższe wersje wymienionych powyżej bibliotek i aplikacji powinny działać równie dobrze, aczkolwiek nie było to testowane.

Uruchomienie
------------
Po instalacji wszystkich zależności należy ściągnąć kod serwisu poleceniem::
    
    git clone http://jakies.repozytorium.pewnie.github

Następnie należy zainstalować bazę danych::
    
    cd wolnelektury/wolnelektury
    ./manage.py syncdb
    
Oraz zaimportować lektury z katalogu books::

    ./manage.py importbooks ../books

Teraz wystarczy uruchomić serwer deweloperski poleceniem::
    
    ./manage.py runserver
    
W wyniku powinniśmy otrzymać całkiem funkcjonalny serwer.

