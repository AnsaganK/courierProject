# Generated by Django 4.1.3 on 2022-11-17 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_executor_date_conclusion_executor_date_terminated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ofc',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ofcs', to='app.city', verbose_name='Город'),
        ),
    ]
