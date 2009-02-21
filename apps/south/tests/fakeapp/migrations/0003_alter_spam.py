from south.db import db
from django.db import models

class Migration:
    
    def forwards(self):
        
        db.alter_column("southtest_spam", 'name', models.CharField(max_length=255, null=True))
    
    def backwards(self):
        
        db.alter_column("southtest_spam", 'name', models.CharField(max_length=255))
