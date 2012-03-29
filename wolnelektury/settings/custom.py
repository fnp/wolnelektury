PAGINATION_INVALID_PAGE_RAISES_404 = True
THUMBNAIL_QUALITY = 95
TRANSLATION_REGISTRY = "wolnelektury.translation"


# seconds until a changes appears in the changes api
API_WAIT = 10

# limit number of filtering tags
MAX_TAG_LIST = 6

NO_BUILD_EPUB = False
NO_BUILD_TXT = False
NO_BUILD_PDF = False
NO_BUILD_MOBI = False
NO_SEARCH_INDEX = False

ALL_EPUB_ZIP = 'wolnelektury_pl_epub'
ALL_PDF_ZIP = 'wolnelektury_pl_pdf'
ALL_MOBI_ZIP = 'wolnelektury_pl_mobi'

CATALOGUE_DEFAULT_LANGUAGE = 'pol'
PUBLISH_PLAN_FEED = 'http://redakcja.wolnelektury.pl/documents/track/editor-proofreading/?published=false'

# limit rate for ebooks creation
CATALOGUE_PDF_RATE_LIMIT = '1/m'
CATALOGUE_EPUB_RATE_LIMIT = '6/m'
CATALOGUE_MOBI_RATE_LIMIT = '5/m'
CATALOGUE_CUSTOMPDF_RATE_LIMIT = '1/m'

# set to 'new' or 'old' to skip time-consuming test
# for TeX morefloats library version
LIBRARIAN_PDF_MOREFLOATS = None
