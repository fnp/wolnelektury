from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Reindex everything.'
    args = ''

    def handle(self, *args, **opts):
        from catalogue.models import Book
        import search
        idx = search.ReusableIndex()
        idx.open()

        if args:
            books = []
            for a in args:
                books += Book.objects.filter(slug=a).all()
        else:
            books = Book.objects.all()
            
        for b in books:
            print b.title
            idx.index_book(b, None)
        print 'Reindexing tags.'
        idx.index_tags()
        idx.close()
