# This file is part of Wolnelektury, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from datetime import date
import os
from .paths import VAR_DIR

# limit number of filtering tags
MAX_TAG_LIST = 6

NO_CUSTOM_PDF = True

CATALOGUE_DEFAULT_LANGUAGE = 'pol'
PUBLISH_PLAN_FEED = 'http://redakcja.wolnelektury.pl/documents/track/editor-proofreading/?published=false'

# limit rate for ebooks creation
CATALOGUE_CUSTOMPDF_RATE_LIMIT = '1/m'

# set to 'new' or 'old' to skip time-consuming test
# for TeX morefloats library version
LIBRARIAN_PDF_MOREFLOATS = None

LATEST_BLOG_POSTS = "https://fundacja.wolnelektury.pl/feed/?cat=-135"

CATALOGUE_COUNTERS_FILE = os.path.join(VAR_DIR, 'catalogue_counters.p')

CATALOGUE_MIN_INITIALS = 60

PICTURE_PAGE_SIZE = 20

PAYU_POS = {
    '300746': {
        'client_secret': '2ee86a66e5d97e3fadc400c9f19b065d',
        'secondary_key': 'b6ca15b0d1020e8094d9b5f8d163db54',
        'sandbox': True,
    },
}

CLUB_PAYU_POS = '300746'
CLUB_PAYU_RECURRING_POS = '300746'
CLUB_APP_HOST = None

CLUB_RETRIES_START = date(2022, 4, 20)
CLUB_RETRY_DAYS_MAX = 90
CLUB_RETRY_DAYS_DAILY = 3
CLUB_RETRY_LESS = 7

CLUB_CONTACT_EMAIL = 'darowizny@wolnelektury.pl'

MESSAGING_MIN_DAYS = 2

NEWSLETTER_PHPLIST_SUBSCRIBE_URL = None


VARIANTS = {
}

EPUB_FUNDRAISING = []

CIVICRM_BASE = None
CIVICRM_KEY = None

CIVICRM_ACTIVITIES = {
    'Contribution': 'Wpłata',
    'Recurring contribution': 'Wpłata cykliczna',
    'Failed contribution': 'Nieudana wpłata',
}

EXPERIMENTS_LAYOUT = 1
EXPERIMENTS_SOWKA = 0
EXPERIMENTS_SEARCH = 0

WIDGETS = {}
