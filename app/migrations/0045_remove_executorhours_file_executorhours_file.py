# Generated by Django 4.1.3 on 2022-12-13 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_executor_bicycle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='executorhours',
            name='file',
        ),
        migrations.AddField(
            model_name='executorhours',
            name='file',
            field=models.ManyToManyField(blank=True, null=True, related_name='executor_hours', to='app.archivefile', verbose_name='Файл'),
        ),
    ]
