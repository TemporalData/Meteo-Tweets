# Generated by Django 3.1.3 on 2021-04-13 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo_map', '0003_auto_20210413_1620'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='geolocation',
            name='geo_id',
        ),
    ]
