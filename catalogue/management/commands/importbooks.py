import os

from django.core.management.base import BaseCommand
from django.core.management.color import color_style
from optparse import make_option

from catalogue.models import Book


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
    )
    help = 'Imports books from the specified directories.'
    args = 'directory [directory ...]'

    def handle(self, *directories, **options):
        from django.db import transaction

        self.style = color_style()

        verbosity = int(options.get('verbosity', 1))
        show_traceback = options.get('traceback', False)

        # Start transaction management.
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)

        for dir_name in directories:
            if not os.path.isdir(dir_name):
                print self.style.ERROR("Skipping '%s': not a directory." % dir_name)
            else:
                for file_name in os.listdir(dir_name):
                    file_path = os.path.join(dir_name, file_name)
                    if not os.path.splitext(file_name)[1] == '.xml':
                        print self.style.NOTICE("Skipping '%s': not an XML file." % file_path)
                        continue
                    if verbosity > 0:
                        print "Parsing '%s'" % file_path
                    
                    Book.from_xml_file(file_path)
        
        transaction.commit()
        transaction.leave_transaction_management()

