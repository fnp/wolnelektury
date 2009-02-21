
from django.db import connection
from django.conf import settings
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):

    """
    MySQL implementation of database operations.
    """
    
    alter_string_set_type = ''
    alter_string_set_null = 'MODIFY %(column)s %(type)s NULL;'
    alter_string_drop_null = 'MODIFY %(column)s %(type)s NOT NULL;'
    drop_index_string = 'DROP INDEX %(index_name)s ON %(table_name)s'
    allows_combined_alters = False
    has_ddl_transactions = False
    
    def execute(self, sql, params=[]):
        if hasattr(settings, "DATABASE_STORAGE_ENGINE") and \
           settings.DATABASE_STORAGE_ENGINE:
            generic.DatabaseOperations.execute(self, "SET storage_engine=%s;" %
                settings.DATABASE_STORAGE_ENGINE)
        return generic.DatabaseOperations.execute(self, sql, params)
    execute.__doc__ = generic.DatabaseOperations.execute.__doc__

    def rename_column(self, table_name, old, new):
        if old == new or self.dry_run:
            return []
        
        qn = connection.ops.quote_name
        
        rows = [x for x in self.execute('DESCRIBE %s' % (qn(table_name),)) if x[0] == old]
        
        if not rows:
            raise ValueError("No column '%s' in '%s'." % (old, table_name))
        
        params = (
            qn(table_name),
            qn(old),
            qn(new),
            rows[0][1],
            rows[0][2] == "YES" and "NULL" or "NOT NULL",
            rows[0][3] == "PRI" and "PRIMARY KEY" or "",
            rows[0][4] and "DEFAULT " or "",
            rows[0][4] and "%s" or "",
            rows[0][5] or "",
        )
        
        sql = 'ALTER TABLE %s CHANGE COLUMN %s %s %s %s %s %s %s %s;' % params
        
        if rows[0][4]:
            self.execute(sql, (rows[0][4],))
        else:
            self.execute(sql)
    
    
    def rename_table(self, old_table_name, table_name):
        """
        Renames the table 'old_table_name' to 'table_name'.
        """
        if old_table_name == table_name:
            # No Operation
            return
        qn = connection.ops.quote_name
        params = (qn(old_table_name), qn(table_name))
        self.execute('RENAME TABLE %s TO %s;' % params)
