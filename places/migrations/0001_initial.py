# Generated by Django 3.2.7 on 2021-10-15 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255, verbose_name='адрес')),
                ('coordinates_lng', models.FloatField(verbose_name='Долгота')),
                ('coordinates_lat', models.FloatField(verbose_name='Широта')),
                ('coordinates_requested', models.DateTimeField(auto_now_add=True, verbose_name='Дата запроса')),
            ],
            options={
                'verbose_name': 'Место',
                'verbose_name_plural': 'Места',
            },
        ),
    ]
