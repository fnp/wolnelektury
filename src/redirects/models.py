from django.db import models
from django.urls import reverse


class Redirect(models.Model):
    slug = models.SlugField(unique=True)
    url = models.CharField(max_length=255)
    counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('redirect', args=[self.slug])

    def update_counter(self):
        type(self).objects.filter(pk=self.pk).update(counter=models.F('counter') + 1)

