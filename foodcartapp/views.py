from django.http import JsonResponse
from django.templatetags.static import static
import json
import pprint

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
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
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


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
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    try:
        request_body = json.loads(request.body.decode())
        pprint.pprint(request_body)
        order = Order.objects.create(address=request_body.get('address'),
                             name=request_body.get('firstname'),
                             surname=request_body.get('lastname'),
                             cellphone_number=request_body.get('phonenumber'))
        for order_item in request_body.get('products'):
            OrderItem.objects.create(quantity=order_item.get('quantity'),
                                     order=order,
                                     product_id=order_item.get('product'))

        return JsonResponse({})

    except ValueError:
        return JsonResponse({
            'error': 'Can not load json!',
        })


