# Generated by Django 4.1.3 on 2022-11-16 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_executor_executor_id_executor_is_terminated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executor',
            name='code',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Код '),
        ),
    ]