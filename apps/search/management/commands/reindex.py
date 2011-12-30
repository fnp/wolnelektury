from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Reindex everything.'
    args = ''

    def handle(self, *args, **opts):
        from catalogue.models import Book
        import search
        idx = search.ReusableIndex()
        idx.open()
        for b in Book.objects.all():
            print b.title
            idx.index_book(b, None)
        print 'Reindexing tags.'
        idx.index_tags()
        idx.close()