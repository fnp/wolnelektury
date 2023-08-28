import csv
from datetime import datetime
from io import StringIO
from django.conf import settings
from django.http import HttpResponse
from django.utils.safestring import mark_safe


def bank_export(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=cp1250')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    writer = csv.writer(response)

    for obj in queryset:
        writer.writerow([
            obj.payment_id,
            obj.full_name,
            '',
            obj.street_address,
            ' '.join([obj.postal_code, obj.town]).strip(),
            obj.iban[2:10],
            obj.iban,
            settings.PZ_NIP,
            'OF'
        ])
    return response


def parse_payment_feedback(f):
    lines = csv.reader(StringIO(f.read().decode('cp1250')))
    for line in lines:
        print(line)
        assert line[0] in ('1', '2')
        if line[0] == '1':
            # Totals line.
            continue
        booking_date = line[3]
        booking_date = datetime.strptime(booking_date, '%Y%m%d')
        payment_id = line[7]
        is_dd = line[16] == 'DD'
        realised = line[17] == '1'
        reject_code = line[18]
        yield payment_id, booking_date, is_dd, realised, reject_code

            


def parse_export_feedback(f):
    # The AU file.
    lines = csv.reader(StringIO(f.read().decode('cp1250')))
    for line in lines:
        payment_id = line[0]
        status = int(line[8])
        comment = line[9]
        yield payment_id, status, comment


        

def bank_order(date, sent_at, queryset):
    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=order.PLD'
    rows = []

    no_dates = []
    no_amounts = []
    cancelled = []

    if date is None:
        raise ValueError('Payment date not set yet.')

    for debit in queryset:
        if debit.bank_acceptance_date is None:
            no_dates.append(debit)
        if debit.amount is None:
            no_amounts.append(debit)
        if debit.cancelled_at and debit.cancelled_at.date() <= date and (sent_at is None or debit.cancelled_at < sent_at):
            cancelled.append(debit)

    if no_dates or no_amounts or cancelled:
        t = ''
        if no_dates:
            t += 'Bank acceptance not received for: '
            t += ', '.join(
                '<a href="/admin/pz/directdebit/{}/change">{}</a>'.format(
                    debit.pk, debit
                )
                for debit in no_dates
            )
            t += '. '
        if no_amounts:
            t += 'Amount not set for: '
            t += ', '.join(
                '<a href="/admin/pz/directdebit/{}/change">{}</a>'.format(
                    debit.pk, debit
                )
                for debit in no_amounts
            )
            t += '. '
        if cancelled:
            t += 'Debits have been cancelled: '
            t += ', '.join(
                '<a href="/admin/pz/directdebit/{}/change">{}</a>'.format(
                    debit.pk, debit
                )
                for debit in cancelled
            )
            t += '. '
        raise ValueError(mark_safe(t))

    for debit in queryset:
        rows.append(
            '{order_code},{date},{amount},{dest_bank_id},0,"{dest_iban}","{user_iban}",'
            '"{dest_addr}","{user_addr}",0,{user_bank_id},'
            '"/NIP/{dest_nip}/IDP/{payment_id}|/TXT/{payment_desc}||",'
            '"","","01"'.format(
                order_code=210,
                date=date.strftime('%Y%m%d'),

                amount=debit.amount * 100,
                dest_bank_id=settings.PZ_IBAN[2:10],
                dest_iban=settings.PZ_IBAN,
                user_iban=debit.iban,
                dest_addr=settings.PZ_ADDRESS_STRING,
                user_bank_id=debit.iban[2:10],
                dest_nip=settings.PZ_NIP,
                payment_id=debit.payment_id,
                payment_desc=settings.PZ_PAYMENT_DESCRIPTION,
                user_addr = '|'.join((
                    debit.full_name,
                    '',
                    debit.street_address,
                    ' '.join((debit.postal_code, debit.town))
                ))
            )
        )
    response.write('\r\n'.join(rows).encode('cp1250'))

    return response
