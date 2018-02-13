# -*- coding: utf-8 -*-
from datetime import date
from lxml import etree
from django.core.management.base import BaseCommand

from isbn.models import ISBNPool, ONIXRecord

ONIXNS = '{http://ns.editeur.org/onix/3.0/reference}'

DIRECT_FIELDS = {
    'product_form': 'ProductForm',
    'product_form_detail': 'ProductFormDetail',
    'title': 'TitleText',
    'part_number': 'PartNumber',
    'edition_type': 'EditionType',
    'edition_number': 'EditionNumber',
    'language': 'LanguageCode',
    'imprint': 'ImprintName',
}

UNNAMED = u'Autor nieznany'


def parse_date(date_str):
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:])
    return date(year, month, day)


def get_descendants(element, tags):
    if isinstance(tags, basestring):
        tags = [tags]
    return element.findall('.//' + '/'.join(ONIXNS + tag for tag in tags))


def get_field(element, tags, allow_multiple=False):
    sub_elements = get_descendants(element, tags)
    if not allow_multiple:
        assert len(sub_elements) <= 1, 'multiple elements: %s' % tags
    return sub_elements[0].text if sub_elements else None


class Command(BaseCommand):
    help = "Import data from ONIX."
    args = 'filename'

    def handle(self, filename, *args, **options):
        tree = etree.parse(open(filename))
        for product in get_descendants(tree, 'Product'):
            isbn = get_field(product, ['ProductIdentifier', 'IDValue'])
            assert len(isbn) == 13
            pool = ISBNPool.objects.get(prefix__in=[isbn[:i] for i in xrange(8, 11)])
            contributors = [
                self.parse_contributor(contributor)
                for contributor in get_descendants(product, 'Contributor')]
            record_data = {
                'isbn_pool': pool,
                'suffix': int(isbn[len(pool.prefix):-1]),
                'publishing_date': parse_date(
                    get_field(product, ['PublishingDate', 'Date'], allow_multiple=True)),
                'contributors': contributors,
            }
            for field, tag in DIRECT_FIELDS.iteritems():
                record_data[field] = get_field(product, tag) or ''
            record = ONIXRecord.objects.create(**record_data)
            ONIXRecord.objects.filter(pk=record.pk).update(datestamp=parse_date(product.attrib['datestamp']))

    @staticmethod
    def parse_contributor(contributor):
        data = {
            'isni': get_field(contributor, 'IDValue'),
            'name': get_field(contributor, 'PersonNameInverted'),
            'corporate_name': get_field(contributor, 'CorporateName'),
            'unnamed': get_field(contributor, 'UnnamedPersons')
        }
        contributor_data = {
            'role': get_field(contributor, 'ContributorRole'),
        }
        for key, value in data.iteritems():
            if value:
                contributor_data[key] = value
        if contributor_data.get('name') == UNNAMED:
            del contributor_data['name']
            contributor_data['unnamed'] = '01'
        for date_elem in get_descendants(contributor, 'ContributorDate'):
            date_role = get_field(date_elem, 'ContributorDateRole')
            date = get_field(date_elem, 'Date')
            if date_role == '50':
                contributor_data['birth_date'] = date
            elif date_role == '51':
                contributor_data['death_date'] = date
        return contributor_data
