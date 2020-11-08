import json
from django.db import models
from wikidata.client import Client


class Entity(models.Model):
    WIKIDATA_PREFIX = 'https://www.wikidata.org/wiki/'
    WIKIDATA_IMAGE = 'P18'
    WIKIDATA_COORDINATE_LOCATION = 'P625'
    WIKIDATA_EARTH = 'Q2'

    uri = models.CharField(max_length=255, unique=True, db_index=True)
    label = models.CharField(max_length=1024, blank=True)
    description = models.CharField(max_length=2048, blank=True)
    wikipedia_link = models.CharField(max_length=1024, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    images = models.TextField(blank=True)

    @property
    def is_interesting(self):
        return self.wikipedia_link or (self.lat and self.lon) or len(self.images)>2
    
    def populate(self):
        if self.uri.startswith(self.WIKIDATA_PREFIX):
            self.populate_from_wikidata(
                self.uri[len(self.WIKIDATA_PREFIX):]
            )

    def populate_from_wikidata(self, wikidata_id):
        client = Client()
        entity = client.get(wikidata_id)

        self.label = entity.label.get('pl', entity.label) or ''
        self.description = entity.description.get('pl', entity.description) or ''
        sitelinks = entity.attributes.get('sitelinks', {})
        self.wikipedia_link = sitelinks.get('plwiki', sitelinks.get('enwiki', {})).get('url') or ''

        location_prop = client.get(self.WIKIDATA_COORDINATE_LOCATION)
        location = entity.get(location_prop)
        if location and location.globe.id == self.WIKIDATA_EARTH:
            self.lat = location.latitude
            self.lon = location.longitude

        images = entity.getlist(client.get(self.WIKIDATA_IMAGE))
        self.images = json.dumps([
            {
                "url": image.image_url,
                "page": image.page_url,
                "resolution": image.image_resolution,
            } for image in images
        ])


class Reference(models.Model):
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    entity = models.ForeignKey(Entity, models.CASCADE)
    first_section = models.CharField(max_length=255)

    class Meta:
        unique_together = (('book', 'entity'),)

