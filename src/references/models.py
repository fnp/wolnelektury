import json
import urllib.parse
from django.db import models
from wikidata.client import Client


class Entity(models.Model):
    WIKIDATA_PREFIX = 'https://www.wikidata.org/wiki/'
    WIKIDATA_IMAGE = 'P18'
    WIKIDATA_COORDINATE_LOCATION = 'P625'
    WIKIDATA_EARTH = 'Q2'
    WIKIDATA_IMAGE_QUERY = './w/api.php?action=query&titles={}&format=json&prop=imageinfo&iiprop=url&iiurlwidth=240&iiurlheight=200'

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
        image_data_list = []
        for image in images:
            image_data = {
                "url": image.image_url,
                "page": image.page_url,
                "resolution": image.image_resolution,
            }

            result = client.request(
                self.WIKIDATA_IMAGE_QUERY.format(
                    urllib.parse.quote(image.title)
                )
            )

            result_data = next(iter(result['query']['pages'].values()))['imageinfo'][0]
            image_data['thumburl'] = result_data['thumburl']
            image_data['thumbresolution'] = [
                result_data['thumbwidth'],
                result_data['thumbheight']
            ]
            if 'responsiveUrls' in result_data:
                image_data['responsiveUrls'] = result_data['responsiveUrls']

            image_data_list.append(image_data)

        self.images = json.dumps(image_data_list)


class Reference(models.Model):
    book = models.ForeignKey('catalogue.Book', models.CASCADE)
    entity = models.ForeignKey(Entity, models.CASCADE)
    first_section = models.CharField(max_length=255)

    class Meta:
        unique_together = (('book', 'entity'),)

