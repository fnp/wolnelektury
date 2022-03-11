from django.db import models


class Edition(models.Model):
    book = models.ForeignKey('Book', models.CASCADE)
    identifier = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)



