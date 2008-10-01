
from django.db import connection
from south.db import generic

class DatabaseOperations(generic.DatabaseOperations):

    """
    SQLite3 implementation of database operations.
    """

    def __init__(self):
        raise NotImplementedError("Support for SQLite3 is not yet complete.")