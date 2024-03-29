# Generated by Django 4.0.8 on 2023-08-28 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('club', '0043_monthlyamount_wide_singleamount_wide'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ambassador',
            options={'ordering': ['name'], 'verbose_name': 'ambasador', 'verbose_name_plural': 'ambasadorowie'},
        ),
        migrations.AlterModelOptions(
            name='club',
            options={'verbose_name': 'towarzystwo', 'verbose_name_plural': 'towarzystwa'},
        ),
        migrations.AlterModelOptions(
            name='membership',
            options={'verbose_name': 'członkostwo', 'verbose_name_plural': 'członkostwa'},
        ),
        migrations.AlterModelOptions(
            name='payucardtoken',
            options={'verbose_name': 'token PayU karty płatniczej', 'verbose_name_plural': 'tokeny PayU kart płatniczych'},
        ),
        migrations.AlterModelOptions(
            name='payunotification',
            options={'verbose_name': 'notyfikacja PayU', 'verbose_name_plural': 'notyfikacje PayU'},
        ),
        migrations.AlterModelOptions(
            name='payuorder',
            options={'verbose_name': 'Zamówienie PayU', 'verbose_name_plural': 'Zamówienia PayU'},
        ),
        migrations.AlterModelOptions(
            name='reminderemail',
            options={'ordering': ['days_before'], 'verbose_name': 'email z przypomnieniem', 'verbose_name_plural': 'e-maile z przypomnieniem'},
        ),
        migrations.AlterModelOptions(
            name='schedule',
            options={'verbose_name': 'harmonogram', 'verbose_name_plural': 'harmonogramy'},
        ),
        migrations.AlterField(
            model_name='ambassador',
            name='name',
            field=models.CharField(max_length=255, verbose_name='imię i nazwisko'),
        ),
        migrations.AlterField(
            model_name='ambassador',
            name='photo',
            field=models.ImageField(blank=True, upload_to='', verbose_name='zdjęcie'),
        ),
        migrations.AlterField(
            model_name='ambassador',
            name='text',
            field=models.CharField(max_length=1024, verbose_name='tekst'),
        ),
        migrations.AlterField(
            model_name='club',
            name='default_monthly_amount',
            field=models.IntegerField(verbose_name='domyślna kwota dla miesięcznych wpłat'),
        ),
        migrations.AlterField(
            model_name='club',
            name='default_single_amount',
            field=models.IntegerField(verbose_name='domyślna kwota dla pojedynczej wpłaty'),
        ),
        migrations.AlterField(
            model_name='club',
            name='min_amount',
            field=models.IntegerField(verbose_name='minimalna kwota'),
        ),
        migrations.AlterField(
            model_name='club',
            name='min_for_year',
            field=models.IntegerField(verbose_name='minimalna kwota na rok'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='utworzone'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='manual',
            field=models.BooleanField(default=False, verbose_name='ustawione ręcznie'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='nazwa'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='notes',
            field=models.CharField(blank=True, max_length=2048, verbose_name='notatki'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='updated_at',
            field=models.DateField(auto_now=True, verbose_name='aktualizacja'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='użytkownik'),
        ),
        migrations.AlterField(
            model_name='payucardtoken',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='utworzony'),
        ),
        migrations.AlterField(
            model_name='payucardtoken',
            name='disposable_token',
            field=models.CharField(max_length=255, verbose_name='token jednorazowy'),
        ),
        migrations.AlterField(
            model_name='payucardtoken',
            name='reusable_token',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='token wielokrotnego użytku'),
        ),
        migrations.AlterField(
            model_name='payunotification',
            name='body',
            field=models.TextField(verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='payunotification',
            name='received_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='odebrana'),
        ),
        migrations.AlterField(
            model_name='payuorder',
            name='customer_ip',
            field=models.GenericIPAddressField(verbose_name='adres IP klienta'),
        ),
        migrations.AlterField(
            model_name='payuorder',
            name='order_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='ID zamówienia'),
        ),
        migrations.AlterField(
            model_name='payuorder',
            name='status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Czeka'), ('WAITING_FOR_CONFIRMATION', 'Czeka na potwierdzenie'), ('COMPLETED', 'Ukończone'), ('CANCELED', 'Anulowane'), ('REJECTED', 'Odrzucone'), ('ERR-INVALID_TOKEN', 'Błędny token')], max_length=128),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body',
            field=models.TextField(verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_de',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_en',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_es',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_fr',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_it',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_lt',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_pl',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_ru',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='body_uk',
            field=models.TextField(null=True, verbose_name='treść'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='days_before',
            field=models.SmallIntegerField(verbose_name='dni przed'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject',
            field=models.CharField(max_length=1024, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_de',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_en',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_es',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_fr',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_it',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_lt',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_pl',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_ru',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='reminderemail',
            name='subject_uk',
            field=models.CharField(max_length=1024, null=True, verbose_name='temat'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='kwota'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='e-mail'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='wygasa'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='is_cancelled',
            field=models.BooleanField(default=False, verbose_name='anulowany'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='key',
            field=models.CharField(max_length=255, unique=True, verbose_name='klucz'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='club.membership', verbose_name='członkostwo'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='method',
            field=models.CharField(choices=[('payu-re', 'PayU recurring'), ('payu', 'PayU'), ('paypal', 'PayPal')], max_length=32, verbose_name='metoda płatności'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='monthly',
            field=models.BooleanField(default=True, verbose_name='miesięcznie'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='payed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='opłacona'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='source',
            field=models.CharField(blank=True, max_length=255, verbose_name='źródło'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='started_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='start'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='yearly',
            field=models.BooleanField(default=False, verbose_name='rocznie'),
        ),
    ]
