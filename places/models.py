from django.db import models
import requests


class Place(models.Model):

    address = models.CharField('адрес', max_length=255, unique=True)
    coordinates_lng = models.FloatField(verbose_name='Долгота', null=True)
    coordinates_lat = models.FloatField(verbose_name='Широта', null=True)
    coordinates_requested = models.DateTimeField('Дата запроса', auto_now_add=True)

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return f"{self.address} {self.coordinates_lng}, {self.coordinates_lat}"


def fetch_coordinates(apikey, address, places_list=[]):

    place = next((item for item in places_list if item['address'] == address), False)

    if place:
        lon = place['coordinates_lng']
        lat = place['coordinates_lat']
        if None in (lon, lat):
            return None
        return float(lat), float(lon)

    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        place = Place.objects.create(address=address, coordinates_lat=None, coordinates_lng=None)
        place.save()
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    new_address = {'address': address, 'coordinates_lat':float(lat), 'coordinates_lng':float(lon)}
    Place.objects.create(**new_address)

    places_list.append(new_address)

    return float(lat), float(lon)
