# Generated by Django 4.0.3 on 2023-10-24 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apilist', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('temperature', models.FloatField()),
            ],
        ),
    ]