# Generated by Django 4.1.3 on 2022-11-19 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_dayhour_executorhours_delete_executorhour_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dayhour',
            options={'ordering': ['pk'], 'verbose_name': 'Часы по дням', 'verbose_name_plural': 'Часы по дням'},
        ),
    ]
