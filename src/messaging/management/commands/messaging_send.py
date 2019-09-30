from django.core.management.base import BaseCommand, CommandError
from messaging.models import EmailTemplate


class Command(BaseCommand):
    help = 'Send emails defined in templates.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Dry run')

    def handle(self, *args, **options):
        for et in EmailTemplate.objects.all():
            et.run(verbose=True, dry_run=options['dry_run'])

