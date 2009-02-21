from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import models
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models.fields import FieldDoesNotExist
from optparse import make_option
from south import migration
import sys
import os
import re
import string
import random
import inspect
import parser

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--model', action='append', dest='model_list', type='string',
            help='Generate a Create Table migration for the specified model.  Add multiple models to this migration with subsequent --model parameters.'),
        make_option('--add-field', action='append', dest='field_list', type='string',
            help='Generate an Add Column migration for the specified modelname.fieldname - you can use this multiple times to add more than one column.'),
        make_option('--initial', action='store_true', dest='initial', default=False,
            help='Generate the initial schema for the app.'),
    )
    help = "Creates a new template migration for the given app"
    
    def handle(self, app=None, name="", model_list=None, field_list=None, initial=False, **options):
        
        # If model_list is None, then it's an empty list
        model_list = model_list or []
        
        # If field_list is None, then it's an empty list
        field_list = field_list or []
        
        # make sure --model and --all aren't both specified
        if initial and (model_list or field_list):
            print "You cannot use --initial and other options together"
            return
            
        # specify the default name 'initial' if a name wasn't specified and we're
        # doing a migration for an entire app
        if not name and initial:
            name = 'initial'
            
        # if not name, there's an error
        if not name:
            print "You must name this migration"
            return
        
        if not app:
            print "Please provide an app in which to create the migration."
            return
            
        # See if the app exists
        app_models_module = models.get_app(app)
        if not app_models_module:
            print "App '%s' doesn't seem to exist, isn't in INSTALLED_APPS, or has no models." % app
            return
            
        # Determine what models should be included in this migration.
        models_to_migrate = []
        if initial:
            models_to_migrate = models.get_models(app_models_module)
            if not models_to_migrate:
                print "No models found in app '%s'" % (app)
                return
        else:
            for model_name in model_list:
                model = models.get_model(app, model_name)
                if not model:
                    print "Couldn't find model '%s' in app '%s'" % (model_name, app)
                    return
                    
                models_to_migrate.append(model)
        
        # See what fields need to be included
        fields_to_add = []
        for field_spec in field_list:
            model_name, field_name = field_spec.split(".", 1)
            model = models.get_model(app, model_name)
            if not model:
                print "Couldn't find model '%s' in app '%s'" % (model_name, app)
                return
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist:
                print "Model '%s' doesn't have a field '%s'" % (model_name, field_name)
                return
            fields_to_add.append((model, field_name, field))
        
        # Make the migrations directory if it's not there
        app_module_path = app_models_module.__name__.split('.')[0:-1]
        try:
            app_module = __import__('.'.join(app_module_path), {}, {}, [''])
        except ImportError:
            print "Couldn't find path to App '%s'." % app
            return
            
        migrations_dir = os.path.join(
            os.path.dirname(app_module.__file__),
            "migrations",
        )
        # Make sure there's a migrations directory and __init__.py
        if not os.path.isdir(migrations_dir):
            print "Creating migrations directory at '%s'..." % migrations_dir
            os.mkdir(migrations_dir)
        init_path = os.path.join(migrations_dir, "__init__.py")
        if not os.path.isfile(init_path):
            # Touch the init py file
            print "Creating __init__.py in '%s'..." % migrations_dir
            open(init_path, "w").close()
        # See what filename is next in line. We assume they use numbers.
        migrations = migration.get_migration_names(migration.get_app(app))
        highest_number = 0
        for migration_name in migrations:
            try:
                number = int(migration_name.split("_")[0])
                highest_number = max(highest_number, number)
            except ValueError:
                pass
        # Make the new filename
        new_filename = "%04i%s_%s.py" % (
            highest_number + 1,
            "".join([random.choice(string.letters.lower()) for i in range(0)]), # Possible random stuff insertion
            name,
        )
        # If there's a model, make the migration skeleton, else leave it bare
        forwards, backwards = '', ''
        if fields_to_add:
            # First, do the added fields
            for model, field_name, field in fields_to_add:
                field_definition = generate_field_definition(model, field)
                
                if isinstance(field, models.ManyToManyField):
                    # Make a mock model for each side
                    mock_model = "\n".join([
                        create_mock_model(model, "        "), 
                        create_mock_model(field.rel.to, "        ")
                    ])
                    # And a field defn, that's actually a table creation
                    forwards += '''
        # Mock Model
%s
        # Adding ManyToManyField '%s.%s'
        db.create_table('%s', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('%s', models.ForeignKey(%s, null=False)),
            ('%s', models.ForeignKey(%s, null=False))
        )) ''' % (
                mock_model,
                model._meta.object_name,
                field.name,
                field.m2m_db_table(),
                field.m2m_column_name()[:-3], # strip off the '_id' at the end
                model._meta.object_name,
                field.m2m_reverse_name()[:-3], # strip off the '_id' at the ned
                field.rel.to._meta.object_name
                )
                    backwards += '''
        # Dropping ManyToManyField '%s.%s'
        db.drop_table('%s')''' % (
                        model._meta.object_name,
                        field.name,
                        field.m2m_db_table()
                    )
                    continue
                elif field.rel: # ForeignKey, etc.
                    mock_model = create_mock_model(field.rel.to, "        ")
                    field_definition = related_field_definition(field, field_definition)
                else:
                    mock_model = None
                
                # If we can't get it (inspect madness?) then insert placeholder
                if not field_definition:
                    print "Warning: Could not generate field definition for %s.%s, manual editing of migration required." % \
                                (model._meta.object_name, field.name)
                    field_definition = '<<< REPLACE THIS WITH FIELD DEFINITION FOR %s.%s >>>' % (model._meta.object_name, f.name)
                
                if mock_model:
                    forwards += '''
        # Mock model
%s
        ''' % (mock_model)
                
                forwards += '''
        # Adding field '%s.%s'
        db.add_column(%r, %r, %s)
        ''' % (
            model._meta.object_name,
            field.name,
            model._meta.db_table,
            field.name,
            field_definition,
        )
                backwards += '''
        # Deleting field '%s.%s'
        db.delete_column(%r, %r)
        ''' % (
            model._meta.object_name,
            field.name,
            model._meta.db_table,
            field.column,
        )
        
        if models_to_migrate:
            # Now, do the added models
            for model in models_to_migrate:
                table_name = model._meta.db_table
                mock_models = []
                fields = []
                for f in model._meta.local_fields:
                    
                    # Look up the field definition to see how this was created
                    field_definition = generate_field_definition(model, f)
                    
                    # If it's a OneToOneField, and ends in _ptr, just use it
                    if isinstance(f, models.OneToOneField) and f.name.endswith("_ptr"):
                        mock_models.append(create_mock_model(f.rel.to, "        "))
                        field_definition = "models.OneToOneField(%s)" % f.rel.to.__name__
                    
                    # It's probably normal then
                    elif field_definition:
                        
                        if isinstance(f, models.ForeignKey):
                            mock_models.append(create_mock_model(f.rel.to, "        "))
                            field_definition = related_field_definition(f, field_definition)
                    
                    # Oh noes, no defn found
                    else:
                        print "Warning: Could not generate field definition for %s.%s, manual editing of migration required." % \
                                (model._meta.object_name, f.name)
                        print f, type(f)
                                
                        field_definition = '<<< REPLACE THIS WITH FIELD DEFINITION FOR %s.%s >>>' % (model._meta.object_name, f.name)
                                                
                    fields.append((f.name, field_definition))
                    
                if mock_models:
                    forwards += '''
        
        # Mock Models
%s
        ''' % "\n".join(mock_models)
        
                forwards += '''
        # Model '%s'
        db.create_table(%r, (
            %s
        ))''' % (
                    model._meta.object_name,
                    table_name,
                    "\n            ".join(["('%s', %s)," % (f[0], f[1]) for f in fields]),
                )

                backwards = ('''db.delete_table('%s')
        ''' % table_name) + backwards
        
                # Now go through local M2Ms and add extra stuff for them
                for m in model._meta.local_many_to_many:
                    # ignore generic relations
                    if isinstance(m, GenericRelation):
                        continue

                    # if the 'through' option is specified, the table will
                    # be created through the normal model creation above.
                    if m.rel.through:
                        continue
                        
                    mock_models = [create_mock_model(model, "        "), create_mock_model(m.rel.to, "        ")]
                    
                    forwards += '''
        # Mock Models
%s
        
        # M2M field '%s.%s'
        db.create_table('%s', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('%s', models.ForeignKey(%s, null=False)),
            ('%s', models.ForeignKey(%s, null=False))
        )) ''' % (
                        "\n".join(mock_models),
                        model._meta.object_name,
                        m.name,
                        m.m2m_db_table(),
                        m.m2m_column_name()[:-3], # strip off the '_id' at the end
                        model._meta.object_name,
                        m.m2m_reverse_name()[:-3], # strip off the '_id' at the ned
                        m.rel.to._meta.object_name
                )
                
                    backwards = '''db.delete_table('%s')
        ''' % m.m2m_db_table() + backwards
                
                if model._meta.unique_together:
                    ut = model._meta.unique_together
                    if not isinstance(ut[0], (list, tuple)):
                        ut = (ut,)
                        
                    for unique in ut:
                        columns = ["'%s'" % model._meta.get_field(f).column for f in unique]
                        
                        forwards += '''
        db.create_index('%s', [%s], unique=True, db_tablespace='%s')
        ''' %   (
                        table_name,
                        ','.join(columns),
                        model._meta.db_tablespace
                )
                
                
            forwards += '''
        
        db.send_create_signal('%s', ['%s'])''' % (
                app, 
                "','".join(model._meta.object_name for model in models_to_migrate)
                )
        
        # Try sniffing the encoding using PEP 0263's method
        encoding = None
        first_two_lines = inspect.getsourcelines(app_models_module)[0][:2]
        for line in first_two_lines:
            if re.search("coding[:=]\s*([-\w.]+)", line):
                encoding = line
        
        if (not forwards) and (not backwards):
            forwards = '"Write your forwards migration here"'
            backwards = '"Write your backwards migration here"'
        fp = open(os.path.join(migrations_dir, new_filename), "w")
        fp.write("""%s
from south.db import db
from django.db import models
from %s.models import *

class Migration:
    
    def forwards(self):
        %s
    
    def backwards(self):
        %s
""" % (encoding or "", '.'.join(app_module_path), forwards, backwards))
        fp.close()
        print "Created %s." % new_filename


def generate_field_definition(model, field):
    """
    Inspects the source code of 'model' to find the code used to generate 'field'
    """
    def test_field(field_definition):
        try:
            parser.suite(field_definition)
            return True
        except SyntaxError:
            return False
            
    def strip_comments(field_definition):
        # remove any comments at the end of the field definition string.
        field_definition = field_definition.strip()
        if '#' not in field_definition:
            return field_definition
            
        index = field_definition.index('#')
        while index:
            stripped_definition = field_definition[:index].strip()
            # if the stripped definition is parsable, then we've removed
            # the correct comment.
            if test_field(stripped_definition):
                return stripped_definition
            
            try:    
                index = field_definition.index('#', index+1)
            except ValueError:
                break
            
        return field_definition
        
    # give field subclasses a chance to do anything tricky
    # with the field definition
    if hasattr(field, 'south_field_definition'):
        return field.south_field_definition()
    
    field_pieces = []
    found_field = False
    source = inspect.getsourcelines(model)
    if not source:
        raise Exception("Could not find source to model: '%s'" % (model.__name__))
    
    # look for a line starting with the field name
    start_field_re = re.compile(r'\s*%s\s*=\s*(.*)' % field.name)
    for line in source[0]:
        # if the field was found during a previous iteration, 
        # we're here because the field spans across multiple lines
        # append the current line and try again
        if found_field:
            field_pieces.append(line.strip())
            if test_field(' '.join(field_pieces)):
                return strip_comments(' '.join(field_pieces))
            continue
        
        match = start_field_re.match(line)
        if match:
            found_field = True
            field_pieces.append(match.groups()[0].strip())
            if test_field(' '.join(field_pieces)):
                return strip_comments(' '.join(field_pieces))
    
    # the 'id' field never gets defined, so return what django does by default
    # django.db.models.options::_prepare
    if field.name == 'id' and field.__class__ == models.AutoField:
        return "models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)"
    
    # search this classes parents
    for base in model.__bases__:
        # we don't want to scan the django base model
        if base == models.Model:
            continue
            
        field_definition = generate_field_definition(base, field)
        if field_definition:
            return field_definition
            
    return None
    
def replace_model_string(field_definition, search_string, model_name):
    # wrap 'search_string' in both ' and " chars when searching
    quotes = ["'", '"']
    for quote in quotes:
        test = "%s%s%s" % (quote, search_string, quote)
        if test in field_definition:
            return field_definition.replace(test, model_name)
            
    return None
        
def related_field_definition(field, field_definition):
    # if the field definition contains any of the following strings,
    # replace them with the model definition:
    #   applabel.modelname
    #   modelname
    #   django.db.models.fields.related.RECURSIVE_RELATIONSHIP_CONSTANT
    strings = [
        '%s.%s' % (field.rel.to._meta.app_label, field.rel.to._meta.object_name),
        '%s' % field.rel.to._meta.object_name,
        RECURSIVE_RELATIONSHIP_CONSTANT
    ]
    
    for test in strings:
        fd = replace_model_string(field_definition, test, field.rel.to._meta.object_name)
        if fd:
            return fd
    
    return field_definition

def create_mock_model(model, indent="        "):
    # produce a string representing the python syntax necessary for creating
    # a mock model using the supplied real model
    if not model._meta.pk.__class__.__module__.startswith('django.db.models.fields'):
        # we can fix this with some clever imports, but it doesn't seem necessary to
        # spend time on just yet
        print "Can't generate a mock model for %s because it's primary key isn't a default django field; it's type %s." % (model, model._meta.pk.__class__)
        sys.exit()
    
    pk_field_args = []
    pk_field_kwargs = {}
    other_mocks = []
    # If it's a OneToOneField or ForeignKey, take it's first arg
    if model._meta.pk.__class__.__name__ in ["OneToOneField", "ForeignKey"]:
        if model._meta.pk.rel.to == model:
            pk_field_args += ["'self'"]
        else:
            pk_field_args += [model._meta.pk.rel.to._meta.object_name]
            other_mocks += [model._meta.pk.rel.to]
    
    # Perhaps it has a max_length set?
    if model._meta.pk.max_length:
        pk_field_kwargs["max_length"] = model._meta.pk.max_length
    
    return "%s%s%s = db.mock_model(model_name='%s', db_table='%s', db_tablespace='%s', pk_field_name='%s', pk_field_type=models.%s, pk_field_args=[%s], pk_field_kwargs=%r)" % \
        (
        "\n".join([create_mock_model(m, indent) for m in other_mocks]+[""]),
        indent,
        model._meta.object_name,
        model._meta.object_name,
        model._meta.db_table,
        model._meta.db_tablespace,
        model._meta.pk.name,
        model._meta.pk.__class__.__name__,
        ", ".join(pk_field_args),
        pk_field_kwargs,
        )
