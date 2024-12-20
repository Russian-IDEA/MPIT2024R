# Generated by Django 4.2.7 on 2024-11-29 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_report_index_alter_yandexoffer_barcode_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='report',
            name='column',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='report',
            name='reason',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='report',
            name='type',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='yandexoffer',
            name='article',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='yandexoffer',
            name='currencyId',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='yandexoffer',
            name='description',
            field=models.CharField(max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='yandexoffer',
            name='name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='yandexoffer',
            name='picture',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='yandexoffer',
            name='vendor',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
