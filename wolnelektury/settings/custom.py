# seconds until a changes appears in the changes api
API_WAIT = 10

# limit number of filtering tags
MAX_TAG_LIST = 6

NO_SEARCH_INDEX = False
NO_CUSTOM_PDF = True

CATALOGUE_DEFAULT_LANGUAGE = 'pol'
PUBLISH_PLAN_FEED = 'http://redakcja.wolnelektury.pl/documents/track/editor-proofreading/?published=false'

# limit rate for ebooks creation
CATALOGUE_CUSTOMPDF_RATE_LIMIT = '1/m'

# set to 'new' or 'old' to skip time-consuming test
# for TeX morefloats library version
LIBRARIAN_PDF_MOREFLOATS = None

FUNDING_DEFAULT = 20
FUNDING_MIN_AMOUNT = 1
