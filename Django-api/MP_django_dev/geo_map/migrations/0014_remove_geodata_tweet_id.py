# Generated by Django 3.1.3 on 2021-01-28 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo_map', '0013_geodata_geo_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geodata',
            name='tweet_id',
        ),
    ]
