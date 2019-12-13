from django.utils.translation import ugettext_lazy as _

PLACE_DEFINITIONS = [
    ('top', _('Top of all pages.'), True),
    ('book-page', _('Book page'), False),
    ('book-text-intermission', _('Book text intermission'), False),
    ('book-fragment-list', _('Next to list of book fragments.'), False),
    ('blackout', _('Blackout'), True),
]

PLACE_CHOICES = [p[:2] for p in PLACE_DEFINITIONS]

PLACES = {
    p[0]: p[2]
    for p in PLACE_DEFINITIONS
}
