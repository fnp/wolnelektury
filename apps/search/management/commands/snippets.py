from django.core.management.base import BaseCommand

from glob import glob
from optparse import make_option
from os import path
from sys import stdout
from django.conf import settings

class Command(BaseCommand):
    help = 'Reindex everything.'
    args = ''

    option_list = BaseCommand.option_list + (
        make_option('-C', '--check-just-read', action='store_true', dest='check', default=False,
            help='Check snippets utf-8'),
        make_option('-c', '--check', action='store_true', dest='check2', default=False,
            help='Check snippets utf-8 by walking through index'),
        )


    def handle(self, *args, **opts):
        from catalogue.models import Book
        import search

        if opts['check']:
            sfn = glob(settings.SEARCH_INDEX+'snippets/*')
            print sfn
            for fn in sfn:
                print fn
                bkid = int(path.basename(fn))
                with open(fn) as f:
                    cont = f.read()
                    try:
                        uc = cont.decode('utf-8')
                    except UnicodeDecodeError, ude:
                        print "error in snippets %d" % bkid
        if opts['check2']:
            s = search.Search()
            reader = s.searcher.getIndexReader()
            numdocs = reader.numDocs()
            for did in range(numdocs):
                doc = reader.document(did)
                if doc and doc.get('book_id'):
                    bkid = int(doc.get('book_id'))
                    #import pdb; pdb.set_trace()
                    stdout.write("\r%d / %d" % (did, numdocs))
                    stdout.flush()
                    ss  = doc.get('snippet_position')
                    sl  = doc.get('snippet_length')
                    if ss and sl:
                        snips = Snippets(bkid)
                        try:
                            txt = snips.get((ss,sl))
                            assert len(txt) == sl
                        except UnicodeDecodeError, ude:
                            stdout.write("\nerror in snippets %d\n" % bkid)
                            raise ude

            stdout.write("\ndone.\n")

