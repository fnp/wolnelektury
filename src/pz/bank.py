import csv
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _


def bank_export(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=cp1250')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)
    writer.writerow([
        'Identyfikator płatności (IDP)',
        'Nazwa Płatnika',
        'Adres Płatnika Ulica + numer domu',
        'Adres Płatnika kod+miejscowość',
        'Numer kierunkowy banku Płatnika',
        'Numer rachunku bankowego Płatnika',
        'Identyfikator Odbiorcy (NIP Odbiorcy)',
        'Osobowość prawna Płatnika (Osoba fizyczna)'
    ])

    # TODO: ansi encoding

    for obj in queryset:
        street_addr = obj.street
        if obj.building:
            street_addr += ' ' + obj.building
        if obj.flat:
            street_addr += ' m. ' + obj.flat
        street_addr = street_addr.strip()
        writer.writerow([
            obj.payment_id,
            ' '.join([obj.first_name, obj.last_name]).strip(),
            street_addr,
            ' '.join([obj.postal_code, obj.town]).strip(),
            obj.iban[2:10],
            obj.iban,
            '9521877087',
            'OF'
        ])
    return response
