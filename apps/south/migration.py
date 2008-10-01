
import datetime
import os
import sys
from django.conf import settings
from django.db import models
from models import MigrationHistory
from south.db import db


def get_app(app):
    """
    Returns the migrations module for the given app model name/module, or None
    if it does not use migrations.
    """
    if isinstance(app, (str, unicode)):
        # If it's a string, use the models module
        app = models.get_app(app)
    mod = __import__(app.__name__[:-7], {}, {}, ['migrations'])
    if hasattr(mod, 'migrations'):
        return getattr(mod, 'migrations')


def get_migrated_apps():
    """
    Returns all apps with migrations.
    """
    for mapp in models.get_apps():
        app = get_app(mapp)
        if app:
            yield app


def get_app_name(app):
    """
    Returns the _internal_ app name for the given app module.
    i.e. for <module django.contrib.auth.models> will return 'auth'
    """
    return app.__name__.split('.')[-2]


def get_app_fullname(app):
    """
    Returns the full python name of an app - e.g. django.contrib.auth
    """
    return app.__name__[:-11]


def short_from_long(app_name):
    return app_name.split(".")[-1]


def get_migration_names(app):
    """
    Returns a list of migration file names for the given app.
    """
    return sorted([
        filename[:-3]
        for filename in os.listdir(os.path.dirname(app.__file__))
        if filename.endswith(".py") and filename != "__init__.py"
    ])


def get_migration_classes(app):
    """
    Returns a list of migration classes (one for each migration) for the app.
    """
    for name in get_migration_names(app):
        yield get_migration(app, name)


def get_migration(app, name):
    """
    Returns the migration class implied by 'name'.
    """
    try:
        module = __import__(app.__name__ + "." + name, '', '', ['Migration'])
        return module.Migration
    except ImportError:
        raise ValueError("Migration %s:%s does not exist." % (get_app_name(app), name))


def all_migrations():
    return dict([
        (app, dict([(name, get_migration(app, name)) for name in get_migration_names(app)]))
        for app in get_migrated_apps()
    ])


def dependency_tree():
    tree = all_migrations()
    
    # Annotate tree with 'backwards edges'
    for app, classes in tree.items():
        for name, cls in classes.items():
            cls.needs = []
            if not hasattr(cls, "needed_by"):
                cls.needed_by = []
            if hasattr(cls, "depends_on"):
                for dapp, dname in cls.depends_on:
                    dapp = get_app(dapp)
                    if dapp not in tree:
                        print "Migration %s in app %s depends on unmigrated app %s." % (
                            name,
                            get_app_name(app),
                            dapp,
                        )
                        sys.exit(1)
                    if dname not in tree[dapp]:
                        print "Migration %s in app %s depends on nonexistent migration %s in app %s." % (
                            name,
                            get_app_name(app),
                            dname,
                            get_app_name(dapp),
                        )
                        sys.exit(1)
                    cls.needs.append((dapp, dname))
                    if not hasattr(tree[dapp][dname], "needed_by"):
                        tree[dapp][dname].needed_by = []
                    tree[dapp][dname].needed_by.append((app, name))
    
    # Sanity check whole tree
    for app, classes in tree.items():
        for name, cls in classes.items():
            cls.dependencies = dependencies(tree, app, name)
    
    return tree


def nice_trace(trace):
    return " -> ".join([str((get_app_name(a), n)) for a, n in trace])


def dependencies(tree, app, name, trace=[]):
    # Copy trace to stop pass-by-ref problems
    trace = trace[:]
    # Sanity check
    for papp, pname in trace:
        if app == papp:
            if pname == name:
                print "Found circular dependency: %s" % nice_trace(trace + [(app,name)])
                sys.exit(1)
            else:
                # See if they depend in the same app the wrong way
                migrations = get_migration_names(app)
                if migrations.index(name) > migrations.index(pname):
                    print "Found a lower migration (%s) depending on a higher migration (%s) in the same app (%s)." % (pname, name, get_app_name(app))
                    print "Path: %s" % nice_trace(trace + [(app,name)])
                    sys.exit(1)
    # Get the dependencies of a migration
    deps = []
    migration = tree[app][name]
    for dapp, dname in migration.needs:
        deps.extend(
            dependencies(tree, dapp, dname, trace+[(app,name)])
        )
    return deps


def remove_duplicates(l):
    m = []
    for x in l:
        if x not in m:
            m.append(x)
    return m


def needed_before_forwards(tree, app, name, sameapp=True):
    """
    Returns a list of migrations that must be applied before (app, name),
    in the order they should be applied.
    Used to make sure a migration can be applied (and to help apply up to it).
    """
    app_migrations = get_migration_names(app)
    needed = []
    if sameapp:
        for aname in app_migrations[:app_migrations.index(name)]:
            needed += needed_before_forwards(tree, app, aname, False)
            needed += [(app, aname)]
    for dapp, dname in tree[app][name].needs:
        needed += needed_before_forwards(tree, dapp, dname)
        needed += [(dapp, dname)]
    return remove_duplicates(needed)


def needed_before_backwards(tree, app, name, sameapp=True):
    """
    Returns a list of migrations that must be unapplied before (app, name) is,
    in the order they should be unapplied.
    Used to make sure a migration can be unapplied (and to help unapply up to it).
    """
    app_migrations = get_migration_names(app)
    needed = []
    if sameapp:
        for aname in reversed(app_migrations[app_migrations.index(name)+1:]):
            needed += needed_before_backwards(tree, app, aname, False)
            needed += [(app, aname)]
    for dapp, dname in tree[app][name].needed_by:
        needed += needed_before_backwards(tree, dapp, dname)
        needed += [(dapp, dname)]
    return remove_duplicates(needed)


def run_forwards(app, migrations, fake=False, silent=False):
    """
    Runs the specified migrations forwards, in order.
    """
    for migration in migrations:
        app_name = get_app_name(app)
        if not silent:
            print " > %s: %s" % (app_name, migration)
        klass = get_migration(app, migration)
        if fake:
            if not silent:
                print "   (faked)"
        else:
            db.start_transaction()
            try:
                klass().forwards()
                db.execute_deferred_sql()
            except:
                db.rollback_transaction()
                raise
            else:
                db.commit_transaction()
        # Record us as having done this
        record = MigrationHistory.for_migration(app_name, migration)
        record.applied = datetime.datetime.utcnow()
        record.save()


def run_backwards(app, migrations, ignore=[], fake=False, silent=False):
    """
    Runs the specified migrations backwards, in order, skipping those
    migrations in 'ignore'.
    """
    for migration in migrations:
        if migration not in ignore:
            app_name = get_app_name(app)
            if not silent:
                print " < %s: %s" % (app_name, migration)
            klass = get_migration(app, migration)
            if fake:
                if not silent:
                    print "   (faked)"
            else:
                db.start_transaction()
                try:
                    klass().backwards()
                    db.execute_deferred_sql()
                except:
                    db.rollback_transaction()
                    raise
                else:
                    db.commit_transaction()
            # Record us as having not done this
            record = MigrationHistory.for_migration(app_name, migration)
            record.delete()


def right_side_of(x, y):
    return left_side_of(reversed(x), reversed(y))


def left_side_of(x, y):
    return list(y)[:len(x)] == list(x)


def forwards_problems(tree, forwards, done, silent=False):
    problems = []
    for app, name in forwards:
        if (app, name) not in done:
            for dapp, dname in needed_before_backwards(tree, app, name):
                if (dapp, dname) in done:
                    if not silent:
                        print " ! Migration (%s, %s) should not have been applied before (%s, %s) but was." % (get_app_name(dapp), dname, get_app_name(app), name)
                    problems.append(((app, name), (dapp, dname)))
    return problems



def backwards_problems(tree, backwards, done, silent=False):
    problems = []
    for app, name in backwards:
        if (app, name) in done:
            for dapp, dname in needed_before_forwards(tree, app, name):
                if (dapp, dname) not in done:
                    if not silent:
                        print " ! Migration (%s, %s) should have been applied before (%s, %s) but wasn't." % (get_app_name(dapp), dname, get_app_name(app), name)
                    problems.append(((app, name), (dapp, dname)))
    return problems


def migrate_app(app, target_name=None, resolve_mode=None, fake=False, yes=False, silent=False):
    
    app_name = get_app_name(app)
    
    db.debug = not silent
    
    # If any of their app names in the DB contain a ., they're 0.2 or below, so migrate em
    longuns = MigrationHistory.objects.filter(app_name__contains=".")
    if longuns:
        for mh in longuns:
            mh.app_name = short_from_long(mh.app_name)
            mh.save()
        if not silent:
            print "- Updated your South 0.2 database."
    
    # Find out what delightful migrations we have
    tree = dependency_tree()
    migrations = get_migration_names(app)
    
    if target_name not in migrations and target_name not in ["zero", None]:
        matches = [x for x in migrations if x.startswith(target_name)]
        if len(matches) == 1:
            target = migrations.index(matches[0]) + 1
            if not silent:
                print " - Soft matched migration %s to %s." % (
                    target_name,
                    matches[0]
                )
            target_name = matches[0]
        elif len(matches) > 1:
            if not silent:
                print " - Prefix %s matches more than one migration:" % target_name
                print "     " + "\n     ".join(matches)
            return
        else:
            if not silent:
                print " ! '%s' is not a migration." % target_name
            return
    
    # Check there's no strange ones in the database
    ghost_migrations = [m for m in MigrationHistory.objects.filter(applied__isnull = False) if get_app(m.app_name) not in tree or m.migration not in tree[get_app(m.app_name)]]
    if ghost_migrations:
        if not silent:
            print " ! These migrations are in the database but not on disk:"
            print "   - " + "\n   - ".join(["%s: %s" % (x.app_name, x.migration) for x in ghost_migrations])
            print " ! I'm not trusting myself; fix this yourself by fiddling"
            print " ! with the south_migrationhistory table."
        return
    
    # Say what we're doing
    if not silent:
        print "Running migrations for %s:" % app_name
    
    # Get the forwards and reverse dependencies for this target
    if target_name == None:
        target_name = migrations[-1]
    if target_name == "zero":
        forwards = []
        backwards = needed_before_backwards(tree, app, migrations[0]) + [(app, migrations[0])]
    else:
        forwards = needed_before_forwards(tree, app, target_name) + [(app, target_name)]
        # When migrating backwards we want to remove up to and including
        # the next migration up in this app (not the next one, that includes other apps)
        try:
            migration_before_here = migrations[migrations.index(target_name)+1]
            backwards = needed_before_backwards(tree, app, migration_before_here) + [(app, migration_before_here)]
        except IndexError:
            backwards = []
    
    # Get the list of currently applied migrations from the db
    current_migrations = [(get_app(m.app_name), m.migration) for m in  MigrationHistory.objects.filter(applied__isnull = False)]
    
    direction = None
    bad = False
    
    # Work out the direction
    applied_for_this_app = list(MigrationHistory.objects.filter(app_name=app_name, applied__isnull=False).order_by("migration"))
    if target_name == "zero":
        direction = -1
    elif not applied_for_this_app:
        direction = 1
    elif migrations.index(target_name) > migrations.index(applied_for_this_app[-1].migration):
        direction = 1
    elif migrations.index(target_name) < migrations.index(applied_for_this_app[-1].migration):
        direction = -1
    else:
        direction = None
    
    # Is the whole forward branch applied?
    missing = [step for step in forwards if step not in current_migrations]
    # If they're all applied, we only know it's not backwards
    if not missing:
        direction = None
    # If the remaining migrations are strictly a right segment of the forwards
    # trace, we just need to go forwards to our target (and check for badness)
    else:
        problems = forwards_problems(tree, forwards, current_migrations, silent=silent)
        if problems:
            bad = True
        direction = 1
    
    # What about the whole backward trace then?
    if not bad:
        missing = [step for step in backwards if step not in current_migrations]
        # If they're all missing, stick with the forwards decision
        if missing == backwards:
            pass
        # If what's missing is a strict left segment of backwards (i.e.
        # all the higher migrations) then we need to go backwards
        else:
            problems = backwards_problems(tree, backwards, current_migrations, silent=silent)
            if problems:
                bad = True
            direction = -1
    
    if bad and resolve_mode not in ['merge']:
        if not silent:
            print " ! Inconsistent migration history"
            print " ! The following options are available:"
            print "    --merge: will just attempt the migration ignoring any potential dependency conflicts."
        sys.exit(1)
    
    if direction == 1:
        if not silent:
            print " - Migrating forwards to %s." % target_name
        for mapp, mname in forwards:
            if (mapp, mname) not in current_migrations:
                run_forwards(mapp, [mname], fake=fake, silent=silent)
    elif direction == -1:
        if not silent:
            print " - Migrating backwards to just after %s." % target_name
        for mapp, mname in backwards:
            if (mapp, mname) in current_migrations:
                run_backwards(mapp, [mname], fake=fake, silent=silent)
    else:
        if not silent:
            print "- Nothing to migrate."