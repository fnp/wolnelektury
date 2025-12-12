PLACE_DEFINITIONS = [
    ('top', 'U góry wszystkich stron', True),
    ('book-page', 'Strona książki', False),
    ('book-page-center', 'Strona książki, środek', False),
    ('book-text-intermission', 'Przerwa w treści książki', False),
    ('book-fragment-list', 'Obok listy fragmentów książki', False),
    ('blackout', 'Blackout', True, (
        ('full', 'Cały ekran'),
#        ('centre', 'Środek ekranu'),
        ('upper', 'Górna połowa ekranu'),
    )),
    ('crisis', 'Kryzysowa', False, (
        ('quiet', 'Spokojny'),
        ('loud', 'Ostry'),
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
            (f'{p[0]}_{s[0]}', f'{p[1]} — {s[1]}')
            for s in p[3]
        ])
