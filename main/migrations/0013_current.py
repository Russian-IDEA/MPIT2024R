# Generated by Django 5.1.3 on 2024-11-29 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_category_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Current',
            fields=[
                ('current', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
    ]
