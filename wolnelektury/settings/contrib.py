HONEYPOT_FIELD_NAME = 'miut'
PAGINATION_INVALID_PAGE_RAISES_404 = True
THUMBNAIL_QUALITY = 95
TRANSLATION_REGISTRY = "wolnelektury.translation"

SOUTH_MIGRATION_MODULES = {
    'getpaid' : 'wolnelektury.migrations.getpaid',
    'payu': 'wolnelektury.migrations.getpaid_payu',
}

GETPAID_ORDER_DESCRIPTION = "{% load funding_tags %}{{ order|sanitize_payment_title }}"
