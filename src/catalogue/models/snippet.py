from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from search.utils import UnaccentSearchVector


class Snippet(models.Model):
    book = models.ForeignKey('Book', models.CASCADE)
    sec = models.IntegerField()
    anchor = models.CharField(max_length=64)
    text = models.TextField()
    search_vector = SearchVectorField()

    class Meta:
        indexes = [
            GinIndex('search_vector', name='search_vector_idx'),
        ]
            
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.search_vector:
            self.update()

    def update(self):
        self.search_vector = UnaccentSearchVector('text')
        self.save()

    @classmethod
    def update_all(cls):
        cls.objects.all().update(search_vector = build_search_vector('text'))
