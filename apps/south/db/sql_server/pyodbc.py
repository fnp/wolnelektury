from django.db import connection
from django.db.models.fields import *
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):
    """
    django-pyodbc (sql_server.pyodbc) implementation of database operations.
    """
    
    add_column_string = 'ALTER TABLE %s ADD %s;'
    alter_string_set_type = 'ALTER COLUMN %(column)s %(type)s'
    allows_combined_alters = False
    delete_column_string = 'ALTER TABLE %s DROP COLUMN %s;'

    def create_table(self, table_name, fields):
        # Tweak stuff as needed
        for name,f in fields:
            if isinstance(f, BooleanField):
                if f.default == True:
                    f.default = 1
                if f.default == False:
                    f.default = 0

        # Run
        generic.DatabaseOperations.create_table(self, table_name, fields)
