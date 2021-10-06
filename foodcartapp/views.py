from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
# import pprint
import re


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
        # pprint.pprint(request.data)
        req_data = request.data
        if 'products' not in req_data:
            return Response({'error': 'products key is not presented'}, status=status.HTTP_400_BAD_REQUEST)
        if 'firstname' not in req_data:
            return Response({'error': 'firstname key is not presented'}, status=status.HTTP_400_BAD_REQUEST)
        if 'lastname' not in req_data:
            return Response({'error': 'lastname key is not presented'}, status=status.HTTP_400_BAD_REQUEST)
        if 'phonenumber' not in req_data:
            return Response({'error': 'phonenumber key is not presented'}, status=status.HTTP_400_BAD_REQUEST)
        if 'address' not in req_data:
            return Response({'error': 'address key is not presented'}, status=status.HTTP_400_BAD_REQUEST)

        products = req_data.get('products')
        if products is None:
            return Response({'error': 'products key is null, list expected'}, status=status.HTTP_400_BAD_REQUEST)
        if req_data.get('firstname') is None:
            return Response({'error': 'firstname key is null, str expected'}, status=status.HTTP_400_BAD_REQUEST)
        if req_data.get('lastname') is None:
            return Response({'error': 'lastname key is null, str expected'}, status=status.HTTP_400_BAD_REQUEST)
        if req_data.get('phonenumber') is None:
            return Response({'error': 'phonenumber key is null, str expected'}, status=status.HTTP_400_BAD_REQUEST)
        if req_data.get('address') is None:
            return Response({'error': 'address key is null, str expected'}, status=status.HTTP_400_BAD_REQUEST)

        if req_data.get('phonenumber') == "":
            return Response({'error': 'phonenumber key is empty'}, status=status.HTTP_400_BAD_REQUEST)

        rule = re.compile(
            r'^(?:(?:(8|\+7)\s*(?:[.-]\s*)?)?(?:\(\s*([1-9]1[01-9]|[1-9][02-8]1|[1-9][02-8][02-9])\s*\)|([1-9]1[02-9]|[2-9][02-8]1|[1-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([1-9]1[02-9]|[2-9][02-9]1|[1-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$')

        # rule = re.compile(r'^(?:(?:(8|\+7)\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$')
        if not rule.search(req_data.get('phonenumber')):
            return Response({'error': 'phonenumber key is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(req_data.get('firstname'), list):
            return Response({'error': 'firstname is list, str expected'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(products, str):
            return Response({'error': 'products key is str, list expected'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(products, list) and not products:
            return Response({'error': 'products list is empty'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(products, list):
            return Response({'error': 'products key is not list'}, status=status.HTTP_400_BAD_REQUEST)

        for order_item in products:
            product_key = order_item.get('product')
            if not Product.objects.filter(id=product_key).exists():
                return Response({'error': f'invalid product key {product_key}'}, status=status.HTTP_400_BAD_REQUEST)


        order = Order.objects.create(address=req_data.get('address'),
                             name=req_data.get('firstname'),
                             surname=req_data.get('lastname'),
                             cellphone_number=req_data.get('phonenumber'))
        for order_item in products:
            OrderItem.objects.create(quantity=order_item.get('quantity'),
                                     order=order,
                                     product_id=order_item.get('product'))

        return Response({'status': 'Order has been created'})

    except ValueError:
        return JsonResponse({
            'error': 'Can not load json!',
        }, status=status.HTTP_400_BAD_REQUEST)


