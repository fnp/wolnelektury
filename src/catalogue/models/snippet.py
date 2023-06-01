from django.db import models
from django.contrib.postgres.search import SearchVector, SearchVectorField
from search.utils import build_search_vector


class Snippet(models.Model):
    book = models.ForeignKey('Book', models.CASCADE)
    sec = models.IntegerField()
    # header_type ?
    # header_span ?
    text = models.TextField()
    search_vector = SearchVectorField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.search_vector:
            self.update()

    def update(self):
        self.search_vector = build_search_vector('text', config='polish') # config=polish
        self.save()

    @classmethod
    def update_all(cls):
        cls.objects.all().update(search_vector = build_search_vector('text'))
