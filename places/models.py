from django.db import models


class Place(models.Model):

    address = models.CharField('адрес', max_length=255, unique=True)
    coordinates_lng = models.FloatField(verbose_name='Долгота')
    coordinates_lat = models.FloatField(verbose_name='Широта')
    coordinates_requested = models.DateTimeField('Дата запроса', auto_now_add=True)

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return f"{self.address} {self.coordinates_lng}, {self.coordinates_lat}"
