# Generated by Django 2.2.19 on 2021-10-11 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pz', '0004_auto_20210929_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankExportFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('csv', models.FileField(upload_to='pz/feedback/')),
            ],
        ),
        migrations.CreateModel(
            name='BankExportFeedbackLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField()),
                ('comment', models.CharField(max_length=255)),
                ('debit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pz.DirectDebit')),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pz.BankExportFeedback')),
            ],
        ),
    ]