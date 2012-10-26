from django.core.management.base import BaseCommand

from optparse import make_option
class Command(BaseCommand):
    help = 'Reindex everything.'
    args = ''
    
    option_list = BaseCommand.option_list + (
        make_option('-n', '--book-id', action='store_true', dest='book_id', default=False,
            help='book id instead of slugs'),
        make_option('-t', '--just-tags', action='store_true', dest='just_tags', default=False,
            help='just reindex tags'),
    )
    def handle(self, *args, **opts):
        from catalogue.models import Book
        import search
        idx = search.Index()
        
        if not opts['just_tags']:
            if args:
                books = []
                for a in args:
                    if opts['book_id']:
                        books += Book.objects.filter(id=int(a)).all()
                    else:
                        books += Book.objects.filter(slug=a).all()
            else:
                books = Book.objects.all()

            try:
                for b in books:
                    print b.title
                    idx.index_book(b)
                    idx.index.commit()
            except:
                idx.index.rollback()
        print 'Reindexing tags.'
        idx.index_tags()
        idx.index.commit()
