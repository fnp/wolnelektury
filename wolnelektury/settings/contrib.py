HONEYPOT_FIELD_NAME = 'miut'
PAGINATION_INVALID_PAGE_RAISES_404 = True
THUMBNAIL_QUALITY = 95

MODELTRANSLATION_DEFAULT_LANGUAGE = 'pl'
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'pl'

SOUTH_MIGRATION_MODULES = {
    'getpaid' : 'wolnelektury.migrations.getpaid',
    'payu': 'wolnelektury.migrations.getpaid_payu',
}

GETPAID_ORDER_DESCRIPTION = "{% load funding_tags %}{{ order|sanitize_payment_title }}"

PIWIK_URL = ''
PIWIK_SITE_ID = 0
PIWIK_TOKEN = ''
