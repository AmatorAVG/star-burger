from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from foodcartapp.models import Order, OrderItem, RestaurantMenuItem
from places.models import Place, fetch_coordinates

from foodcartapp.models import Product, Restaurant
from django.conf import settings
from geopy import distance


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    YANDEX_KEY = getattr(settings, "YANDEX_KEY")

    order_items = OrderItem.objects.filter(order__status='N').values_list('order_id', 'product_id')
    restaurant_menu = list(RestaurantMenuItem.objects.filter(availability=True))

    unprocessed_orders_with_price = Order.orders.with_price().unprocessed()

    addresses = set(unprocessed_orders_with_price.values_list('address', flat=True))
    addresses.update(set(Restaurant.objects.values_list('address', flat=True)))

    places = list(Place.objects.filter(address__in=addresses).values('address', 'coordinates_lat', 'coordinates_lng'))

    for order in unprocessed_orders_with_price:
        order_product_ids = [product_id for order_id, product_id in order_items if order_id == order.id]

        burger_restaurants = [{rest_item.restaurant for rest_item in restaurant_menu if product_id == rest_item.product_id}
                              for product_id in order_product_ids]

        order.restaurants = list()
        if burger_restaurants:
            total_restaurants = set.intersection(*burger_restaurants)

            for rest in total_restaurants:
                rest_coord = fetch_coordinates(YANDEX_KEY, rest.address, places)
                if not rest_coord:
                    order.restaurants.append([f'{rest} - адрес ресторана не найден', float("inf")])
                    continue
                order_coord = fetch_coordinates(YANDEX_KEY, order.address, places)
                if not order_coord:
                    order.restaurants.append([f'{rest} - адрес заказа не найден', float("inf")])
                    continue
                order_dist = distance.distance(rest_coord, order_coord).km
                order.restaurants.append([f'{rest} - {round(order_dist, 3)} км.', order_dist])
            order.restaurants.sort(key=lambda dist: dist[1])

    return render(request, template_name='order_items.html', context={
       'order_items': unprocessed_orders_with_price,
    })
