��          �      �           	  4     �   R  �   �  
   �     �  �   �  {   ?  r   �     .     7  
   F     Q  %   m     �  }   �  
   -  P   8  b   �     �  $   �     "  2  '     Z  $   n  �   �  ]   	  
   |	     �	  �   �	  u   
  U   �
     �
     �
                &     9  k   K     �  O   �  R     	   b  !   l     �                                                                              
                   	       API WolneLektury.pl API Wolnych Lektur zawiera następujące adresy URL: API serwisu WolneLektury.pl znajduje się pod adresem <code>%(u)s</code>. Za jego pomocą można uzyskać informacje o utworach, ich fragmentach i metadanych. Aby spośród wszystkich pasujących wybrać tylko utwory najwyższego poziomu (pomijając ich podutwory), można użyć zapytania /parent_books/, np.: Audiobooki DAISY Dane domyślnie są serializowane w formacie JSON, ale dostępny jest też format XML – wystarczy dodać parametr <code>?format=xml</code> do dowolnego zapytania. Każdy element na tych listach zawiera adres (w atrybucie „href”), pod którym można znaleźć szczegółowe dane, np. Każdy element uzyskanej listy w atrybucie „href” zawiera link do szczegółowego opisu danego fragmentu, np.: Kolekcje Lista autorów Lista epok Lista gatunków literackich Lista motywów i tematów literackich Lista rodzajów literackich Można łączyć autorów, epoki, gatunki i rodzaje, aby wybrać tylko utwory odpowiadające zadanym kryteriom. Na przykład: Potwierdź Potwierdź dostęp do Wolnych Lektur jako użytkownik <strong>%(user)s</strong>. W ten sam sposób, filtrując dodatkowo według lektur lub motywów, można wyszukiwać fragmenty: Wszystkie utwory Zezwól na dostęp do Wolnych Lektur albo Project-Id-Version: WolneLektury-api
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2023-08-27 23:11+0200
Last-Translator: 
Language-Team: 
Language: en
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Generator: Poedit 3.0.1
 WolneLektury.pl API The URLs in WolneLektury.pl API are: WolneLektury.pl API resides under <code>%(u)s</code>.You can use it to access information about books, their fragments and their metadata. If you only want top-level books and not all the children, you can use /parent_books/, as in: Audiobooks DAISY Default data serialization format is JSON, but you can also use XML by appending <code>?format=xml</code> query parameter to each URL. Each element of those lists contains a link (in a "href") attibutewhich points to individual resource's details, e.g. Again, each entry has a "href" attribute which links to the fragment's details, e.g.: Collections List of all authors List of all epochs List of all genres List of all themes List of all kinds You can combine authors, epochs, genres and kinds to find only books matching those criteria. For instance: Confirm Confirm to authorize access to Wolne Lektury as user <strong>%(user)s</strong>. The same way, using also books and themes, you can search for a list of fragments: All books Authorize access to Wolne Lektury or 