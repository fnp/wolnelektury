# Generated by Django 2.2.19 on 2021-10-12 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pz', '0005_bankexportfeedback_bankexportfeedbackline'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('sent', models.DateTimeField(blank=True, null=True)),
                ('debits', models.ManyToManyField(to='pz.DirectDebit')),
            ],
        ),
    ]
