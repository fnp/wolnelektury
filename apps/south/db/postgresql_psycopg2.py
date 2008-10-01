
from django.db import connection
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):

    """
    PsycoPG2 implementation of database operations.
    """

    def rename_column(self, table_name, old, new):
        if old == new:
            return []
        qn = connection.ops.quote_name
        params = (qn(table_name), qn(old), qn(new))
        self.execute('ALTER TABLE %s RENAME COLUMN %s TO %s;' % params)
    
    def rename_table(self, old_table_name, table_name):
        # First, rename the table
        generic.DatabaseOperations.rename_table(self, old_table_name, table_name)
        # Then, try renaming the ID sequence
        # (if you're using other AutoFields... your problem, unfortunately)
        self.commit_transaction()
        self.start_transaction()
        try:
            generic.DatabaseOperations.rename_table(self, old_table_name+"_id_seq", table_name+"_id_seq")
        except:
            print "   ~ No such sequence (ignoring error)"
            self.rollback_transaction()
        else:
            self.commit_transaction()
        self.start_transaction()