from django.http import JsonResponse
from django.templatetags.static import static
import json
import pprint

from .models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    return Response([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ])


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


@api_view(['POST'])
def register_order(request):
    try:
        # request_body = json.loads(request.body.decode())
        pprint.pprint(request.data)
        order = Order.objects.create(address=request.data.get('address'),
                             name=request.data.get('firstname'),
                             surname=request.data.get('lastname'),
                             cellphone_number=request.data.get('phonenumber'))
        for order_item in request.data.get('products'):
            OrderItem.objects.create(quantity=order_item.get('quantity'),
                                     order=order,
                                     product_id=order_item.get('product'))

        return Response({'status': 'Order has been created'})

    except ValueError:
        return JsonResponse({
            'error': 'Can not load json!',
        })


