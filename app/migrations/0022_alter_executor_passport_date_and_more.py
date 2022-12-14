# Generated by Django 4.1.3 on 2022-11-17 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_alter_executor_date_conclusion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executor',
            name='passport_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата выдачи паспорта'),
        ),
        migrations.AlterField(
            model_name='executor',
            name='passport_place',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Место выдачи паспорта'),
        ),
    ]
