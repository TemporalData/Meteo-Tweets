# Generated by Django 3.1.3 on 2021-01-28 12:42

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo_map', '0011_auto_20210128_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geolocation',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
