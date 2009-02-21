from django.core import management
from django.core.management.commands import test
from django.core.management.commands import syncdb

class Command(test.Command):
    
    def handle(self, *args, **kwargs):
        # point at the core syncdb command when creating tests
        # tests should always be up to date with the most recent model structure
        management.get_commands()
        management._commands['syncdb'] = 'django.core'
        super(Command, self).handle(*args, **kwargs)