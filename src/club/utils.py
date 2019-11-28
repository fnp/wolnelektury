from datetime import timedelta


def add_year(date):
    return date.replace(year=date.year + 1)

def add_month(date):
    day = date.day
    date = (date.replace(day=1) + timedelta(31)).replace(day=1) + timedelta(day - 1)
    if date.day != day:
        date = date.replace(day=1)
    return date

