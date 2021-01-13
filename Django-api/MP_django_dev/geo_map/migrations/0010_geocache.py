# Generated by Django 3.1.3 on 2020-12-13 20:46

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo_map', '0009_auto_20201207_1534'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.TextField()),
                ('data_list', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
            ],
        ),
    ]
