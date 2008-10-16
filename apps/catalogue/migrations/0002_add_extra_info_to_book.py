from south.db import db
from catalogue.fields import JSONField

class Migration:
    
    def forwards(self):
        db.add_column('catalogue_book', 'extra_info', JSONField())
    
    def backwards(self):
        db.delete_column('catalogue_book', 'extra_info')

