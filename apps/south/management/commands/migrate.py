from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.conf import settings
from django.db import models
from optparse import make_option
from south import migration
import sys

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--skip', action='store_true', dest='skip', default=False,
            help='Will skip over out-of-order missing migrations'),
        make_option('--merge', action='store_true', dest='merge', default=False,
            help='Will run out-of-order missing migrations as they are - no rollbacks.'),
        make_option('--only', action='store_true', dest='only', default=False,
            help='Only runs or rolls back the migration specified, and none around it.'),
        make_option('--fake', action='store_true', dest='fake', default=False,
            help="Pretends to do the migrations, but doesn't actually execute them."),
    )
    help = "Runs migrations for all apps."

    def handle(self, app=None, target=None, skip=False, merge=False, only=False, backwards=False, fake=False, **options):
        
        # Work out what the resolve mode is
        resolve_mode = merge and "merge" or (skip and "skip" or None)
        # Turn on db debugging
        from south.db import db
        db.debug = True
        
        # NOTE: THIS IS DUPLICATED FROM django.core.management.commands.syncdb
        # This code imports any module named 'management' in INSTALLED_APPS.
        # The 'management' module is the preferred way of listening to post_syncdb
        # signals, and since we're sending those out with create_table migrations,
        # we need apps to behave correctly.
        for app_name in settings.INSTALLED_APPS:
            try:
                __import__(app_name + '.management', {}, {}, [''])
            except ImportError, exc:
                msg = exc.args[0]
                if not msg.startswith('No module named') or 'management' not in msg:
                    raise
        # END DJANGO DUPE CODE
        
        # Migrate each app
        if app:
            apps = [migration.get_app(app)]
        else:
            apps = migration.get_migrated_apps()
        for app in apps:
            migration.migrate_app(
                app,
                resolve_mode = resolve_mode,
                target_name = target,
                fake = fake,
            )
