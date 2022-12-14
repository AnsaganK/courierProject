# Generated by Django 4.1.3 on 2022-12-29 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0056_alter_userpayment_options_alter_userpayment_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bicycle',
            name='code',
        ),
        migrations.AddField(
            model_name='bicycle',
            name='name',
            field=models.CharField(blank=True, max_length=256, null=True, unique=True, verbose_name='Название велосипеда'),
        ),
        migrations.AlterField(
            model_name='executor',
            name='bicycle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='executors', to='app.bicycle'),
        ),
        migrations.AlterField(
            model_name='executor',
            name='curator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='executors', to=settings.AUTH_USER_MODEL, verbose_name='Куратор'),
        ),
    ]
