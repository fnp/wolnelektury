# Generated by Django 4.0.8 on 2023-08-28 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annoy', '0014_fundraising'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ('place', '-priority'), 'verbose_name': 'banner', 'verbose_name_plural': 'bannery'},
        ),
        migrations.AlterModelOptions(
            name='dynamictextinsert',
            options={'ordering': ('paragraphs',), 'verbose_name': 'dynamiczna wstawka', 'verbose_name_plural': 'dynamiczne wstawki'},
        ),
        migrations.AlterField(
            model_name='banner',
            name='action_label',
            field=models.CharField(blank=True, help_text='Jeśli pusta, cały banner będzie służył jako link.', max_length=255, verbose_name='etykieta akcji'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='close_label',
            field=models.CharField(blank=True, max_length=255, verbose_name='etykieta zamykania'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.FileField(blank=True, upload_to='annoy/banners/', verbose_name='obraz'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='only_authenticated',
            field=models.BooleanField(default=False, verbose_name='tylko dla zalogowanych'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='open_label',
            field=models.CharField(blank=True, max_length=255, verbose_name='etykieta otwierania'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='place',
            field=models.SlugField(choices=[('top', 'U góry wszystkich stron'), ('book-page', 'Strona książki'), ('book-text-intermission', 'Przerwa w treści książki'), ('book-fragment-list', 'Obok listy fragmentów książki'), ('blackout', 'Blackout')], verbose_name='miejsce'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='priority',
            field=models.PositiveSmallIntegerField(default=0, help_text='Bannery z wyższym priorytetem mają pierwszeństwo.', verbose_name='priorytet'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='show_members',
            field=models.BooleanField(default=False, verbose_name='widoczny dla członków klubu'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='since',
            field=models.DateTimeField(blank=True, null=True, verbose_name='od'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='smallfont',
            field=models.BooleanField(default=False, verbose_name='mały font'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='staff_preview',
            field=models.BooleanField(default=False, verbose_name='podgląd tylko dla zespołu'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='style',
            field=models.CharField(blank=True, choices=[('blackout_full', 'Cały ekran'), ('blackout_upper', 'Górna połowa ekranu')], help_text='Dotyczy blackoutu.', max_length=255, verbose_name='styl'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text',
            field=models.TextField(verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_de',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_en',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_es',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_fr',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_it',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_lt',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_pl',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='text_uk',
            field=models.TextField(null=True, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='do'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='url',
            field=models.CharField(max_length=1024, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='dynamictextinsert',
            name='paragraphs',
            field=models.IntegerField(verbose_name='akapity'),
        ),
        migrations.AlterField(
            model_name='dynamictextinserttext',
            name='text',
            field=models.TextField(verbose_name='tekst'),
        ),
    ]
