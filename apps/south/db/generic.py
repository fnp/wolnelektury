
from django.core.management.color import no_style
from django.db import connection, transaction, models
from django.db.backends.util import truncate_name
from django.dispatch import dispatcher
from django.conf import settings

class DatabaseOperations(object):

    """
    Generic SQL implementation of the DatabaseOperations.
    Some of this code comes from Django Evolution.
    """

    def __init__(self):
        self.debug = False
        self.deferred_sql = []


    def execute(self, sql, params=[]):
        """
        Executes the given SQL statement, with optional parameters.
        If the instance's debug attribute is True, prints out what it executes.
        """
        cursor = connection.cursor()
        if self.debug:
            print "   = %s" % sql, params
        cursor.execute(sql, params)
        try:
            return cursor.fetchall()
        except:
            return []
            
            
    def add_deferred_sql(self, sql):
        """
        Add a SQL statement to the deferred list, that won't be executed until
        this instance's execute_deferred_sql method is run.
        """
        self.deferred_sql.append(sql)
        
        
    def execute_deferred_sql(self):
        """
        Executes all deferred SQL, resetting the deferred_sql list
        """
        for sql in self.deferred_sql:
            self.execute(sql)
            
        self.deferred_sql = []


    def create_table(self, table_name, fields):
        """
        Creates the table 'table_name'. 'fields' is a tuple of fields,
        each repsented by a 2-part tuple of field name and a
        django.db.models.fields.Field object
        """
        qn = connection.ops.quote_name
        columns = [
            self.column_sql(table_name, field_name, field)
            for field_name, field in fields
        ]
        
        self.execute('CREATE TABLE %s (%s);' % (qn(table_name), ', '.join([col for col in columns if col])))
    
    add_table = create_table # Alias for consistency's sake


    def rename_table(self, old_table_name, table_name):
        """
        Renames the table 'old_table_name' to 'table_name'.
        """
        if old_table_name == table_name:
            # No Operation
            return
        qn = connection.ops.quote_name
        params = (qn(old_table_name), qn(table_name))
        self.execute('ALTER TABLE %s RENAME TO %s;' % params)


    def delete_table(self, table_name):
        """
        Deletes the table 'table_name'.
        """
        qn = connection.ops.quote_name
        params = (qn(table_name), )
        self.execute('DROP TABLE %s;' % params)
    
    drop_table = delete_table


    def add_column(self, table_name, name, field):
        """
        Adds the column 'name' to the table 'table_name'.
        Uses the 'field' paramater, a django.db.models.fields.Field instance,
        to generate the necessary sql
        
        @param table_name: The name of the table to add the column to
        @param name: The name of the column to add
        @param field: The field to use
        """
        qn = connection.ops.quote_name
        sql = self.column_sql(table_name, name, field)
        if sql:
            params = (
                qn(table_name),
                sql,
            )
            sql = 'ALTER TABLE %s ADD COLUMN %s;' % params
            self.execute(sql)
    
    
    alter_string_set_type = 'ALTER COLUMN %(column)s TYPE %(type)s'
    alter_string_set_null = 'ALTER COLUMN %(column)s SET NOT NULL'
    alter_string_drop_null = 'ALTER COLUMN %(column)s DROP NOT NULL'
    
    def alter_column(self, table_name, name, field):
        """
        Alters the given column name so it will match the given field.
        Note that conversion between the two by the database must be possible.
        
        @param table_name: The name of the table to add the column to
        @param name: The name of the column to alter
        @param field: The new field definition to use
        """
        
        # hook for the field to do any resolution prior to it's attributes being queried
        if hasattr(field, 'south_init'):
            field.south_init()
        
        qn = connection.ops.quote_name
        
        # First, change the type
        params = {
            "column": qn(name),
            "type": field.db_type(),
        }
        sqls = [self.alter_string_set_type % params]
        
        
        # Next, set any default
        params = (
            qn(name),
        )
        
        if not field.null and field.has_default():
            default = field.get_default()
            if isinstance(default, basestring):
                default = "'%s'" % default
            params += ("SET DEFAULT %s",)
        else:
            params += ("DROP DEFAULT",)
        
        sqls.append('ALTER COLUMN %s %s ' % params)
        
        
        # Next, nullity
        params = {
            "column": qn(name),
            "type": field.db_type(),
        }
        if field.null:
            sqls.append(self.alter_string_drop_null % params)
        else:
            sqls.append(self.alter_string_set_null % params)
        
        
        # TODO: Unique
        
        self.execute("ALTER TABLE %s %s;" % (qn(table_name), ", ".join(sqls)))


    def column_sql(self, table_name, field_name, field, tablespace=''):
        """
        Creates the SQL snippet for a column. Used by add_column and add_table.
        """
        qn = connection.ops.quote_name
        
        field.set_attributes_from_name(field_name)
        
        # hook for the field to do any resolution prior to it's attributes being queried
        if hasattr(field, 'south_init'):
            field.south_init()
        
        sql = field.db_type()
        if sql:        
            field_output = [qn(field.column), sql]
            field_output.append('%sNULL' % (not field.null and 'NOT ' or ''))
            if field.primary_key:
                field_output.append('PRIMARY KEY')
            elif field.unique:
                field_output.append('UNIQUE')
        
            tablespace = field.db_tablespace or tablespace
            if tablespace and connection.features.supports_tablespaces and field.unique:
                # We must specify the index tablespace inline, because we
                # won't be generating a CREATE INDEX statement for this field.
                field_output.append(connection.ops.tablespace_sql(tablespace, inline=True))
            
            sql = ' '.join(field_output)
            sqlparams = ()
            # if the field is "NOT NULL" and a default value is provided, create the column with it
            # this allows the addition of a NOT NULL field to a table with existing rows
            if not field.null and field.has_default():
                default = field.get_default()
                if isinstance(default, basestring):
                    default = "'%s'" % default.replace("'", "''")
                sql += " DEFAULT %s"
                sqlparams = (default)
            
            if field.rel:
                self.add_deferred_sql(
                    self.foreign_key_sql(
                        table_name,
                        field.column,
                        field.rel.to._meta.db_table,
                        field.rel.to._meta.get_field(field.rel.field_name).column
                    )
                )
            
            if field.db_index and not field.unique:
                self.add_deferred_sql(self.create_index_sql(table_name, [field.column]))
            
        if hasattr(field, 'post_create_sql'):
            style = no_style()
            for stmt in field.post_create_sql(style, table_name):
                self.add_deferred_sql(stmt)

        if sql:
            return sql % sqlparams
        else:
            return None
        
    def foreign_key_sql(self, from_table_name, from_column_name, to_table_name, to_column_name):
        """
        Generates a full SQL statement to add a foreign key constraint
        """
        constraint_name = '%s_refs_%s_%x' % (from_column_name, to_column_name, abs(hash((from_table_name, to_table_name))))
        return 'ALTER TABLE %s ADD CONSTRAINT %s FOREIGN KEY (%s) REFERENCES %s (%s)%s;' % (
            from_table_name,
            truncate_name(constraint_name, connection.ops.max_name_length()),
            from_column_name,
            to_table_name,
            to_column_name,
            connection.ops.deferrable_sql() # Django knows this
        )
        
    def create_index_name(self, table_name, column_names):
        """
        Generate a unique name for the index
        """
        index_unique_name = ''
        if len(column_names) > 1:
            index_unique_name = '_%x' % abs(hash((table_name, ','.join(column_names))))

        return '%s_%s%s' % (table_name, column_names[0], index_unique_name)

    def create_index_sql(self, table_name, column_names, unique=False, db_tablespace=''):
        """
        Generates a create index statement on 'table_name' for a list of 'column_names'
        """
        if not column_names:
            print "No column names supplied on which to create an index"
            return ''
            
        if db_tablespace and connection.features.supports_tablespaces:
            tablespace_sql = ' ' + connection.ops.tablespace_sql(db_tablespace)
        else:
            tablespace_sql = ''
        
        index_name = self.create_index_name(table_name, column_names)
        qn = connection.ops.quote_name
        return 'CREATE %sINDEX %s ON %s (%s)%s;' % (
            unique and 'UNIQUE ' or '',
            index_name,
            table_name,
            ','.join([qn(field) for field in column_names]),
            tablespace_sql
            )
        
    def create_index(self, table_name, column_names, unique=False, db_tablespace=''):
        """ Executes a create index statement """
        sql = self.create_index_sql(table_name, column_names, unique, db_tablespace)
        self.execute(sql)


    def delete_index(self, table_name, column_names, db_tablespace=''):
        """
        Deletes an index created with create_index.
        This is possible using only columns due to the deterministic
        index naming function which relies on column names.
        """
        name = self.create_index_name(table_name, column_names)
        sql = "DROP INDEX %s" % name
        self.execute(sql)


    def delete_column(self, table_name, name):
        """
        Deletes the column 'column_name' from the table 'table_name'.
        """
        qn = connection.ops.quote_name
        params = (qn(table_name), qn(name))
        self.execute('ALTER TABLE %s DROP COLUMN %s CASCADE;' % params, [])


    def rename_column(self, table_name, old, new):
        """
        Renames the column 'old' from the table 'table_name' to 'new'.
        """
        raise NotImplementedError("rename_column has no generic SQL syntax")


    def start_transaction(self):
        """
        Makes sure the following commands are inside a transaction.
        Must be followed by a (commit|rollback)_transaction call.
        """
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)


    def commit_transaction(self):
        """
        Commits the current transaction.
        Must be preceded by a start_transaction call.
        """
        transaction.commit()
        transaction.leave_transaction_management()


    def rollback_transaction(self):
        """
        Rolls back the current transaction.
        Must be preceded by a start_transaction call.
        """
        transaction.rollback()
        transaction.leave_transaction_management()
    
    
    def send_create_signal(self, app_label, model_names):
        """
        Sends a post_syncdb signal for the model specified.
        
        If the model is not found (perhaps it's been deleted?),
        no signal is sent.
        
        TODO: The behavior of django.contrib.* apps seems flawed in that
        they don't respect created_models.  Rather, they blindly execute
        over all models within the app sending the signal.  This is a
        patch we should push Django to make  For now, this should work.
        """
        app = models.get_app(app_label)
        if not app:
            return
            
        created_models = []
        for model_name in model_names:
            model = models.get_model(app_label, model_name)
            if model:
                created_models.append(model)
                
        if created_models:
            # syncdb defaults -- perhaps take these as options?
            verbosity = 1
            interactive = True
            
            if hasattr(dispatcher, "send"):
                dispatcher.send(signal=models.signals.post_syncdb, sender=app,
                app=app, created_models=created_models,
                verbosity=verbosity, interactive=interactive)
            else:
                models.signals.post_syncdb.send(sender=app,
                app=app, created_models=created_models,
                verbosity=verbosity, interactive=interactive)
                
    def mock_model(self, model_name, db_table, db_tablespace='', 
                    pk_field_name='id', pk_field_type=models.AutoField,
                    pk_field_kwargs={}):
        """
        Generates a MockModel class that provides enough information
        to be used by a foreign key/many-to-many relationship.
        
        Migrations should prefer to use these rather than actual models
        as models could get deleted over time, but these can remain in
        migration files forever.
        """
        class MockOptions(object):
            def __init__(self):
                self.db_table = db_table
                self.db_tablespace = db_tablespace or settings.DEFAULT_TABLESPACE
                self.object_name = model_name
                self.module_name = model_name.lower()

                if pk_field_type == models.AutoField:
                    pk_field_kwargs['primary_key'] = True

                self.pk = pk_field_type(**pk_field_kwargs)
                self.pk.set_attributes_from_name(pk_field_name)
                self.abstract = False

            def get_field_by_name(self, field_name):
                # we only care about the pk field
                return (self.pk, self.model, True, False)

            def get_field(self, name):
                # we only care about the pk field
                return self.pk

        class MockModel(object):
            _meta = None

        # We need to return an actual class object here, not an instance
        MockModel._meta = MockOptions()
        MockModel._meta.model = MockModel
        return MockModel
