# -*- coding: utf-8 -*-
from south.db import db
from django.db import models


class Migration:    
    def forwards(self):
        db.add_column('catalogue_tag', 'death', models.IntegerField(blank=True,  null=True))
    
    def backwards(self):
        db.delete_column('catalogue_tag', 'death')


