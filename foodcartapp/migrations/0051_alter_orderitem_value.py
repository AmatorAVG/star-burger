# Generated by Django 3.2.7 on 2021-10-21 04:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_alter_order_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='value',
            field=models.DecimalField(decimal_places=2, max_digits=9, validators=[django.core.validators.MinValueValidator(0)], verbose_name='стоимость'),
        ),
    ]
