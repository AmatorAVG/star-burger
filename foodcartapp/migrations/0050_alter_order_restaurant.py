# Generated by Django 3.2.7 on 2021-10-21 04:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_alter_order_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
    ]
