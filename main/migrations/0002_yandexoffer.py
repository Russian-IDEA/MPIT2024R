# Generated by Django 4.2.7 on 2024-11-29 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='YandexOffer',
            fields=[
                ('index', models.IntegerField(primary_key=True, serialize=False)),
                ('available', models.BooleanField()),
                ('price', models.FloatField()),
                ('currencyId', models.CharField(max_length=50)),
                ('categoryId', models.IntegerField()),
                ('picture', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('vendor', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=50)),
                ('barcode', models.IntegerField()),
                ('article', models.IntegerField()),
                ('rating', models.FloatField()),
                ('review_amount', models.IntegerField()),
                ('sale', models.FloatField()),
                ('newby', models.BooleanField()),
            ],
        ),
    ]
