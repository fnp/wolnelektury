��          �      �           	  4     �   R  �   �  
   �     �  �   �  {   ?  r   �     .     7  
   F     Q  %   m     �  }   �  
   -  P   8  b   �     �  $   �     "  �  '  "   �  >   	  �   W	  �   W
     N     c  5  i  �   �  �   y     /     B     ^  2   t  %   �  ,   �  �   �     �  �   �  �   x     "  6   B     y                                                                              
                   	       API WolneLektury.pl API Wolnych Lektur zawiera następujące adresy URL: API serwisu WolneLektury.pl znajduje się pod adresem <code>%(u)s</code>. Za jego pomocą można uzyskać informacje o utworach, ich fragmentach i metadanych. Aby spośród wszystkich pasujących wybrać tylko utwory najwyższego poziomu (pomijając ich podutwory), można użyć zapytania /parent_books/, np.: Audiobooki DAISY Dane domyślnie są serializowane w formacie JSON, ale dostępny jest też format XML – wystarczy dodać parametr <code>?format=xml</code> do dowolnego zapytania. Każdy element na tych listach zawiera adres (w atrybucie „href”), pod którym można znaleźć szczegółowe dane, np. Każdy element uzyskanej listy w atrybucie „href” zawiera link do szczegółowego opisu danego fragmentu, np.: Kolekcje Lista autorów Lista epok Lista gatunków literackich Lista motywów i tematów literackich Lista rodzajów literackich Można łączyć autorów, epoki, gatunki i rodzaje, aby wybrać tylko utwory odpowiadające zadanym kryteriom. Na przykład: Potwierdź Potwierdź dostęp do Wolnych Lektur jako użytkownik <strong>%(user)s</strong>. W ten sam sposób, filtrując dodatkowo według lektur lub motywów, można wyszukiwać fragmenty: Wszystkie utwory Zezwól na dostęp do Wolnych Lektur albo Project-Id-Version: WolneLektury-api
Report-Msgid-Bugs-To: 
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 API сервиса WolneLektury.pl API ресурса WolneLektury.pl принадлежат URL: API сервиса WolneLektury.pl расположен по адресу <code>%(u)s</code>.
С его помощью вы можете искать информацию о произведениях, отрывках из них и метаданных.         Чтобы из списка всех релевантных выбрать наиболее точно отвечающие критериям, вы можете можно задавать вопросы/parent_books/, например: Аудиокниги DAISY По умолчанию данные сериализуются в формате JSON,
        но также можно использовать формат XML требуется добавить параметр <code>?format=xml</code>
        параметр запроса для каждого URL.         Каждый элемент списка содержит ссылку (in a "href") attibute
        по которой можно перейти к подробной информации, например:         Каждый элемент найденного списка "href" содержит ссылку, ведущую кподробному описанию, например: Коллекции Список авторов Список эпох Список литературных жанров Список сюжетов и тем Список видов литературы         Можно сочетать авторов, эпохи, жанры и виды для поиска книгиmatching
        Отвечающие заданным критериям. например: Подтверждаю Подтверждение для авторизации доступа к Wolne Lektury как пользователь <strong>%(user)s </strong>.         Тем же способом, используя выбирая книги или сюжеты, можно искать в спискепо фрагментам: Все произведения Авторизация доступа к Wolne Lektury или 