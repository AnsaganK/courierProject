# Generated by Django 4.1.3 on 2022-11-11 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_executor_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Текстовый пароль'),
        ),
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='patronymic',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Отчество'),
        ),
    ]
