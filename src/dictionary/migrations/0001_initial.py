from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anchor', models.CharField(max_length=64)),
                ('html', models.TextField()),
                ('sort_key', models.CharField(max_length=128, db_index=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogue.Book')),
            ],
            options={
                'ordering': ['sort_key'],
            },
            bases=(models.Model,),
        ),
    ]
