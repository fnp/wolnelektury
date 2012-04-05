
from django.core.management.base import BaseCommand
from search import Index, Search
from lucene import IndexReader, IndexSearcher, Term
from catalogue.models import Book


class Command(BaseCommand):
    help = 'Optimize Lucene search index'
    args = ''

    def delete_old(self, index):
        existing_ids = set([book.id for book in Book.objects.all()])

        reader = IndexReader.open(index.index, False)
        searcher = IndexSearcher(reader)
        try:
            num = searcher.docFreq(Term('is_book', 'true'))
            docs = searcher.search(Search.make_term_query(['true'], 'is_book'), num)
            for result in docs.scoreDocs:
                stored = searcher.doc(result.doc)
                book_id = int(stored.get('book_id'))
                if not book_id in existing_ids:
                    print "book id %d doesn't exist." % book_id
                    index.remove_book(book_id)
        finally:
            searcher.close()
            reader.close()

    def handle(self, *args, **opts):
        index = Index()
        index.open()

        self.delete_old(index)

        try:
            index.optimize()
        finally:
            index.close()
