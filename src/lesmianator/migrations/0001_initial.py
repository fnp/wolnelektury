from django.db import models, migrations
import django.db.models.deletion
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Continuations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pickle', models.FileField(upload_to='lesmianator', verbose_name='Continuations file')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Poem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(max_length=120, verbose_name='Slug')),
                ('text', models.TextField(verbose_name='text')),
                ('created_from', jsonfield.fields.JSONField(null=True, verbose_name='Additional information', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('seen_at', models.DateTimeField(auto_now_add=True, verbose_name='last view date')),
                ('view_count', models.IntegerField(default=1, verbose_name='view count')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='continuations',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
