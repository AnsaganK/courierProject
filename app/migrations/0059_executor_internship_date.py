# Generated by Django 4.1.3 on 2023-01-09 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_paymentforcurators_paid_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='executor',
            name='internship_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата начала стажировки'),
        ),
    ]
