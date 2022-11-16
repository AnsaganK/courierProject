# Generated by Django 4.1.3 on 2022-11-16 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_archivefile'),
    ]

    operations = [
        migrations.AddField(
            model_name='executor',
            name='executor_id',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True, verbose_name='Идентификатор'),
        ),
        migrations.AddField(
            model_name='executor',
            name='is_terminated',
            field=models.BooleanField(default=False, verbose_name='Расторгнут'),
        ),
        migrations.AlterField(
            model_name='executor',
            name='code',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, unique=True, verbose_name='Код '),
        ),
        migrations.AlterField(
            model_name='executor',
            name='first_name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='executor',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активен'),
        ),
    ]