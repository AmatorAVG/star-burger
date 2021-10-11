# Generated by Django 3.2.7 on 2021-10-11 09:58

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20211006_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость'),
        ),
    ]
