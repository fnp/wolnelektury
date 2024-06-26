# Generated by Django 4.0.8 on 2024-02-21 11:55

from django.db import migrations, models


def populate_spent(apps, schema_editor):
    Offer = apps.get_model('funding', 'Offer')
    Spent = apps.get_model('funding', 'Spent')
    Book = apps.get_model('catalogue', 'Book')
    for o in Offer.objects.all():
        if Spent.objects.filter(book__slug=o.slug).exists():
            continue
        s = o.funding_set.exclude(completed_at=None).aggregate(s=models.Sum('amount'))['s'] or 0
        if s >= o.target:
            try:
                book = Book.objects.get(slug=o.slug)
                link = ''
            except Book.DoesNotExist:
                book = None
                link = o.slug
            Spent.objects.create(
                book=book,
                link=link,
                amount=o.target,
                timestamp=o.end,
                annotation='auto'
            )


class Migration(migrations.Migration):

    dependencies = [
        ('funding', '0012_spent_annotation_spent_link_alter_spent_book'),
    ]

    operations = [
        migrations.RunPython(
            populate_spent,
            migrations.RunPython.noop
        )
    ]
