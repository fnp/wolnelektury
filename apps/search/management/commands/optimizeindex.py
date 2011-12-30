
from django.core.management.base import BaseCommand
from search import Index

class Command(BaseCommand):
    help = 'Optimize Lucene search index'
    args = ''

    def handle(self, *args, **opts):
        index = Index()
        index.open()
        try:
            index.optimize()
        finally:
            index.close()
