import unittest
import datetime
import sys
import os

from south import migration

# Add the tests directory so fakeapp is on sys.path
test_root = os.path.dirname(__file__)
sys.path.append(test_root)


class TestMigrationLogic(unittest.TestCase):

    """
    Tests if the various logic functions in migration actually work.
    """

    def create_fake_app(self, name):
        
        class Fake:
            pass
        
        fake = Fake()
        fake.__name__ = name
        return fake


    def create_test_app(self):
        
        class Fake:
            pass
        
        fake = Fake()
        fake.__name__ = "fakeapp.migrations"
        fake.__file__ = os.path.join(test_root, "fakeapp", "migrations", "__init__.py")
        return fake
    
    
    def monkeypatch(self):
        """Swaps out various Django calls for fake ones for our own nefarious purposes."""
        
        def new_get_apps():
            return ['fakeapp']
        
        from django.db import models
        from django.conf import settings
        models.get_apps_old, models.get_apps = models.get_apps, new_get_apps
        settings.INSTALLED_APPS, settings.OLD_INSTALLED_APPS = (
            ["fakeapp"],
            settings.INSTALLED_APPS,
        )
        self.redo_app_cache()
    setUp = monkeypatch
    
    
    def unmonkeypatch(self):
        """Undoes what monkeypatch did."""
        
        from django.db import models
        from django.conf import settings
        models.get_apps = models.get_apps_old
        settings.INSTALLED_APPS = settings.OLD_INSTALLED_APPS
        self.redo_app_cache()
    tearDown = unmonkeypatch
    
    
    def redo_app_cache(self):
        from django.db.models.loading import AppCache
        a = AppCache()
        a.loaded = False
        a._populate()
    

    def test_get_app_name(self):
        self.assertEqual(
            "southtest",
            migration.get_app_name(self.create_fake_app("southtest.migrations")),
        )
        self.assertEqual(
            "baz",
            migration.get_app_name(self.create_fake_app("foo.bar.baz.migrations")),
        )
    
    
    def test_get_migrated_apps(self):
        
        P1 = __import__("fakeapp.migrations", {}, {}, [''])
        
        self.assertEqual(
            [P1],
            list(migration.get_migrated_apps()),
        )
    
    
    def test_get_app(self):
        
        P1 = __import__("fakeapp.migrations", {}, {}, [''])
        
        self.assertEqual(P1, migration.get_app("fakeapp"))
        self.assertEqual(P1, migration.get_app(self.create_fake_app("fakeapp.models")))
    
    
    def test_get_app_fullname(self):
        self.assertEqual(
            "southtest",
            migration.get_app_fullname(self.create_fake_app("southtest.migrations")),
        )
        self.assertEqual(
            "foo.bar.baz",
            migration.get_app_fullname(self.create_fake_app("foo.bar.baz.migrations")),
        )
    
    
    def test_get_migration_names(self):
        
        app = self.create_test_app()
        
        self.assertEqual(
            ["0001_spam", "0002_eggs", "0003_alter_spam"],
            migration.get_migration_names(app),
        )
    
    
    def test_get_migration_classes(self):
        
        app = self.create_test_app()
        
        # Can't use vanilla import, modules beginning with numbers aren't in grammar
        M1 = __import__("fakeapp.migrations.0001_spam", {}, {}, ['Migration']).Migration
        M2 = __import__("fakeapp.migrations.0002_eggs", {}, {}, ['Migration']).Migration
        M3 = __import__("fakeapp.migrations.0003_alter_spam", {}, {}, ['Migration']).Migration
        
        self.assertEqual(
            [M1, M2, M3],
            list(migration.get_migration_classes(app)),
        )
    
    
    def test_get_migration(self):
        
        app = self.create_test_app()
        
        # Can't use vanilla import, modules beginning with numbers aren't in grammar
        M1 = __import__("fakeapp.migrations.0001_spam", {}, {}, ['Migration']).Migration
        M2 = __import__("fakeapp.migrations.0002_eggs", {}, {}, ['Migration']).Migration
        
        self.assertEqual(M1, migration.get_migration(app, "0001_spam"))
        self.assertEqual(M2, migration.get_migration(app, "0002_eggs"))
        
        self.assertRaises((ImportError, ValueError), migration.get_migration, app, "0001_jam")
    
    
    def test_all_migrations(self):
        
        app = migration.get_app("fakeapp")
        
        self.assertEqual(
            {app: {
                "0001_spam": migration.get_migration(app, "0001_spam"),
                "0002_eggs": migration.get_migration(app, "0002_eggs"),
                "0003_alter_spam": migration.get_migration(app, "0003_alter_spam"),
            }},
            migration.all_migrations(),
        )
    
    
    def assertListEqual(self, list1, list2):
        list1 = list(list1)
        list2 = list(list2)
        list1.sort()
        list2.sort()
        return self.assertEqual(list1, list2)
    
    
    def test_apply_migrations(self):
        
        app = migration.get_app("fakeapp")
        
        # We should start with no migrations
        self.assertEqual(list(migration.MigrationHistory.objects.all()), [])
        
        # Apply them normally
        migration.migrate_app(app, target_name=None, resolve_mode=None, fake=False, silent=True)
        
        # We should finish with all migrations
        self.assertListEqual(
            (
                (u"fakeapp", u"0001_spam"),
                (u"fakeapp", u"0002_eggs"),
                (u"fakeapp", u"0003_alter_spam"),
            ),
            migration.MigrationHistory.objects.values_list("app_name", "migration"),
        )
        
        # Now roll them backwards
        migration.migrate_app(app, target_name="zero", resolve_mode=None, fake=False, silent=True)
        
        # Finish with none
        self.assertEqual(list(migration.MigrationHistory.objects.all()), [])
    
    
    def test_migration_merge_forwards(self):
        
        app = migration.get_app("fakeapp")
        
        # We should start with no migrations
        self.assertEqual(list(migration.MigrationHistory.objects.all()), [])
        
        # Insert one in the wrong order
        migration.MigrationHistory.objects.create(
            app_name = "fakeapp",
            migration = "0002_eggs",
            applied = datetime.datetime.now(),
        )
        
        # Did it go in?
        self.assertListEqual(
            (
                (u"fakeapp", u"0002_eggs"),
            ),
            migration.MigrationHistory.objects.values_list("app_name", "migration"),
        )
        
        # Apply them normally
        try:
            migration.migrate_app(app, target_name=None, resolve_mode=None, fake=False, silent=True)
        except SystemExit:
            pass
        
        # Nothing should have changed (no merge mode!)
        self.assertListEqual(
            (
                (u"fakeapp", u"0002_eggs"),
            ),
            migration.MigrationHistory.objects.values_list("app_name", "migration"),
        )
        
        # Apply with merge
        migration.migrate_app(app, target_name=None, resolve_mode="merge", fake=False, silent=True)
        
        # We should finish with all migrations
        self.assertListEqual(
            (
                (u"fakeapp", u"0001_spam"),
                (u"fakeapp", u"0002_eggs"),
                (u"fakeapp", u"0003_alter_spam"),
            ),
            migration.MigrationHistory.objects.values_list("app_name", "migration"),
        )
        
        # Now roll them backwards
        migration.migrate_app(app, target_name="0002", resolve_mode=None, fake=False, silent=True)
        migration.migrate_app(app, target_name="0001", resolve_mode=None, fake=True, silent=True)
        migration.migrate_app(app, target_name="zero", resolve_mode=None, fake=False, silent=True)
        
        # Finish with none
        self.assertEqual(list(migration.MigrationHistory.objects.all()), [])
    
    def test_alter_column_null(self):
        def null_ok():
            from django.db import connection, transaction
            # the DBAPI introspection module fails on postgres NULLs.
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO southtest_spam (id, weight, expires, name) VALUES (100, 10.1, now(), NULL);")
            except:
                transaction.rollback()
                return False
            else:
                cursor.execute("DELETE FROM southtest_spam")
                transaction.commit()
                return True
        
        app = migration.get_app("fakeapp")
        self.assertEqual(list(migration.MigrationHistory.objects.all()), [])
        
        # by default name is NOT NULL
        migration.migrate_app(app, target_name="0002", resolve_mode=None, fake=False, silent=True)
        self.failIf(null_ok())
        
        # after 0003, it should be NULL
        migration.migrate_app(app, target_name="0003", resolve_mode=None, fake=False, silent=True)
        self.assert_(null_ok())

        # make sure it is NOT NULL again
        migration.migrate_app(app, target_name="0002", resolve_mode=None, fake=False, silent=True)
        self.failIf(null_ok(), 'name not null after migration')
        
        # finish with no migrations, otherwise other tests fail...
        migration.migrate_app(app, target_name="zero", resolve_mode=None, fake=False, silent=True)
        self.assertEqual(list(migration.MigrationHistory.objects.all()), [])