# Generated by Django 4.2.7 on 2024-11-29 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_yandexoffer_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='column',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='report',
            name='index',
            field=models.BigIntegerField(default=0),
        ),
    ]