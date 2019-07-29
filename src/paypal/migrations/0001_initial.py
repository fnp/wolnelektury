from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingAgreement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agreement_id', models.CharField(max_length=32)),
                ('active', models.BooleanField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='BillingPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plan_id', models.CharField(max_length=32)),
                ('amount', models.IntegerField(unique=True, db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='billingagreement',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='paypal.BillingPlan'),
        ),
        migrations.AddField(
            model_name='billingagreement',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
