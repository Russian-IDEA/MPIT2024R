# Generated by Django 4.2.7 on 2024-11-29 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_report_advice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yandexoffer',
            name='article',
            field=models.CharField(max_length=100, null=True),
        ),
    ]