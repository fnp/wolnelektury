from django.db import models


class Partner(models.Model):
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    def get_price(self, pages):
        price_obj = self.pricelevel_set.exclude(
            min_pages__gt=pages
        ).order_by('-price').first()
        if price_obj is None:
            return None
        return price_obj.price


class PriceLevel(models.Model):
    partner = models.ForeignKey(Partner, models.CASCADE)
    min_pages = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ('price',)
