from south.db import db
from django.db.models import FileField

class Migration:
    
    def forwards(self):
        db.add_column('catalogue_book', 'mp3_file', FileField())
        db.add_column('catalogue_book', 'ogg_file', FileField())
    
    def backwards(self):
        db.delete_column('catalogue_book', 'mp3_file')
        db.delete_column('catalogue_book', 'ogg_file')

