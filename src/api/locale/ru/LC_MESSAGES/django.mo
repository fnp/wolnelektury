��          �      l      �  �   �  �   �  4   N    �  �   �  �  1  	     
     !   '     I     U  O   ]     �     �     �     �     �     �          &  �  +  -  �	  !  �
  I     �  R  �      n  �     l     �  6   �     �     �  �        �     �     �  2   �  ,     %   /  "   U     x     	                                          
                                                   
        Each element of those lists contains a link (in a "href") attibute
        which points to individual resource's details, i.e.:
        <a href="%(e1)s">%(e1)s</a> or
        <a href="%(e2)s">%(e2)s</a>.
       
        If you only want top-level books and not all the children, you can use /parent_books/, as in:
        <a href="%(e)s">%(e)s</a>.
       
        The URLs in WolneLektury.pl API are:
       
        The same way, using also books and themes, you can search for a list of fragments:
        <a href="%(e)s">%(e)s</a>.
        Again, each entry has a "href" attribute which links to the fragment's details, i.e.:
        <a href="%(f)s">%(f)s</a>.
       
        You can combine authors, epochs, genres and kinds to find only books matching
        those criteria. For instance:
        <a href="%(e)s">%(e)s</a>.
       API сервиса WolneLektury.pl расположен по адресу <code>%(u)s</code>.
С его помощью вы можете искать информацию о произведениях, отрывках из них и метаданных and
        Default data serialization format is
        <a href="http://en.wikipedia.org/wiki/JSON">JSON</a>,
        but you can also use XML by appending <code>?format=xml</code>
        query parameter to each URL.
       All books Audiobooks Authorize access to Wolne Lektury Collections Confirm Confirm to authorize access to Wolne Lektury as user <strong>%(user)s</strong>. DAISY List of all authors List of all epochs List of all genres List of all kinds List of all themes WolneLektury.pl API slug Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
 
        Каждый элемент списка содержит ссылку (in a "href") attibute
        по которой можно перейти к подробной информации, например:
        <a href="%(e1)s">%(e1)s</a> or
        <a href="%(e2)s">%(e2)s</a>.
       
        Чтобы из списка всех релевантных выбрать наиболее точно отвечающие критериям, вы можете можно задавать вопросы/parent_books/, например:
        <a href="%(e)s">%(e)s</a>.
       
        API ресурса WolneLektury.pl принадлежат URL:
  
        Тем же способом, используя выбирая книги или сюжеты, можно искать в спискепо фрагментам:
        <a href="%(e)s">%(e)s</a>.
        Каждый элемент найденного списка "href" содержит ссылку, ведущую кподробному описанию, например:
        <a href="%(f)s">%(f)s</a>.
       
        Можно сочетать авторов, эпохи, жанры и виды для поиска книгиmatching
        Отвечающие заданным критериям. например:
        <a href="%(e)s">%(e)s</a>.
       По умолчанию данные сериализуются в формате        <a href="http://en.wikipedia.org/wiki/JSON">JSON</a>,
        но также можно использовать формат XML требуется добавить параметр <code>?format=xml</code>
        параметр запроса для каждого URL.
  Все произведения Аудиокниги Авторизация доступа к Wolne Lektury Коллекции Подтверждаю Подтверждение для авторизации доступа к Wolne Lektury как пользователь <strong>%(user)s </strong>. DAISY Список авторов Список эпох Список литературных жанров Список видов литературы Список сюжетов и тем API сервиса WolneLektury.pl slug 