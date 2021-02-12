# Generated by Django 3.1.3 on 2021-02-11 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TermType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typename', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='WeatherTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(blank=True, max_length=30)),
                ('ttype', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='text.termtype')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_idx', models.IntegerField(blank=True)),
                ('user_name', models.CharField(blank=True, max_length=50)),
                ('pub_date', models.DateField()),
                ('text', models.TextField(blank=True)),
                ('raw', models.TextField(blank=True)),
                ('terms', models.ManyToManyField(blank=True, to='text.WeatherTerm')),
            ],
            options={
                'ordering': ['pub_date', 'doc_idx'],
            },
        ),
    ]
