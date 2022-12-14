# Generated by Django 4.1.3 on 2022-12-23 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_city_short_name_alter_city_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='identifier',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Идентификатор'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='type',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Тип'),
        ),
    ]
