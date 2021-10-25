from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from foodcartapp.models import Order, OrderItem, RestaurantMenuItem
from places.models import Place
from django.db.models import Sum, F

from foodcartapp.models import Product, Restaurant
import requests
from django.conf import settings
from geopy import distance
from django.core.exceptions import ObjectDoesNotExist


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    try:
        place = Place.objects.get(address=address)
        lon = place.coordinates_lng
        lat = place.coordinates_lat
        if None in (lon, lat):
            return None

    except ObjectDoesNotExist:
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

        place = Place.objects.create(address=address, coordinates_lat=float(lat), coordinates_lng=float(lon))
        place.save()

    return float(lat), float(lon)


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    YANDEX_KEY = getattr(settings, "YANDEX_KEY")

    order_items = OrderItem.objects.values_list('order_id', 'product_id')
    restaurant_menu = list(RestaurantMenuItem.objects.filter(availability=True))

    orders = Order.objects.annotate(cost=Sum(F('order_items__cost'))).filter(status='N')
    for order in orders:
        order_products = [item[1] for item in order_items if item[0] == order.id]

        burger_restaurants = [{rest_item.restaurant for rest_item in restaurant_menu if product == rest_item.product_id}
                              for product in order_products]

        if len(burger_restaurants):
            total_restaurants = burger_restaurants[0]
            for burger_restaurant in burger_restaurants:
                total_restaurants &= burger_restaurant
            order.restaurants = list()

            for rest in total_restaurants:
                rest_coord = fetch_coordinates(YANDEX_KEY, rest.address)
                if rest_coord is None:
                    order.restaurants.append([f'{rest} - адрес ресторана не найден', 999999])
                    continue
                order_coord = fetch_coordinates(YANDEX_KEY, order.address)
                if order_coord is None:
                    order.restaurants.append([f'{rest} - адрес заказа не найден', 999999])
                    continue
                order_dist = distance.distance(rest_coord, order_coord).km
                order.restaurants.append([f'{rest} - {round(order_dist, 3)} км.', order_dist])
            order.restaurants.sort(key=lambda dist: dist[1])
        else:
            order.restaurants = set()
    return render(request, template_name='order_items.html', context={
       'order_items': orders,
    })
