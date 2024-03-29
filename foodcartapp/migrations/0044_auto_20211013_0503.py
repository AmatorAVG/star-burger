# Generated by Django 3.2.7 on 2021-10-13 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='called',
            field=models.DateTimeField(blank=True, null=True, verbose_name='позвонить'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered',
            field=models.DateTimeField(blank=True, null=True, verbose_name='доставлен'),
        ),
        migrations.AddField(
            model_name='order',
            name='registered',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='зарегистрирован'),
        ),
    ]
