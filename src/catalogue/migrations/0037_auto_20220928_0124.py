# Generated by Django 2.2.28 on 2022-09-27 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0036_book_toc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmedia',
            name='type',
            field=models.CharField(choices=[('mp3', 'MP3 file'), ('ogg', 'Ogg Vorbis file'), ('daisy', 'DAISY file'), ('audio.epub', 'EPUB+audio file')], db_index=True, max_length=20, verbose_name='type'),
        ),
    ]
