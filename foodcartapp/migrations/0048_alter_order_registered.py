# Generated by Django 3.2.7 on 2021-10-21 04:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20211021_0405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='registered',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='зарегистрирован'),
            preserve_default=False,
        ),
    ]
