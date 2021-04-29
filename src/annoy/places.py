from django.utils.translation import ugettext_lazy as _

PLACE_DEFINITIONS = [
    ('top', _('Top of all pages.'), True),
    ('book-page', _('Book page'), False),
    ('book-text-intermission', _('Book text intermission'), False),
    ('book-fragment-list', _('Next to list of book fragments.'), False),
    ('blackout', _('Blackout'), True, (
        ('full', _('Full screen')),
#        ('centre', _('Centre of screen')),
        ('upper', _('Upper half of screen')),
    )),
]

PLACE_CHOICES = [p[:2] for p in PLACE_DEFINITIONS]

PLACES = {
    p[0]: p[2]
    for p in PLACE_DEFINITIONS
}


STYLES = []
for p in PLACE_DEFINITIONS:
    if len(p) > 3:
        STYLES.extend([
            (f'{p[0]}_{s[0]}', s[1])
            for s in p[3]
        ])
