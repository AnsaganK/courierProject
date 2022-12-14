# Generated by Django 4.1.3 on 2022-11-17 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_delete_executorfile_remove_executor_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='executor',
            name='date_conclusion',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата заключения'),
        ),
        migrations.AddField(
            model_name='executor',
            name='date_terminated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата расторжения'),
        ),
        migrations.AddField(
            model_name='executor',
            name='individual',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Физическое лицо'),
        ),
        migrations.AddField(
            model_name='executor',
            name='main_contract',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Основной контракт'),
        ),
        migrations.AddField(
            model_name='executor',
            name='med_exam_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата медкомиссии'),
        ),
        migrations.AddField(
            model_name='executor',
            name='note',
            field=models.TextField(blank=True, null=True, verbose_name='Примечание'),
        ),
        migrations.AddField(
            model_name='executor',
            name='partner',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Партнер'),
        ),
        migrations.AddField(
            model_name='executor',
            name='passport_date',
            field=models.DateField(blank=True, max_length=256, null=True, verbose_name='Дата выдачи паспорта'),
        ),
        migrations.AddField(
            model_name='executor',
            name='passport_place',
            field=models.DateField(blank=True, max_length=256, null=True, verbose_name='Место выдачи паспорта'),
        ),
        migrations.AddField(
            model_name='executor',
            name='passport_series',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Серия и номер паспорта'),
        ),
        migrations.AlterField(
            model_name='executor',
            name='education',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Образование'),
        ),
    ]
