from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
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
        req_data = request.data
        if 'products' not in req_data:
            return Response({'error': 'product key is not presented'}, status=status.HTTP_400_BAD_REQUEST)
        if req_data.get('products') is None:
            return Response({'error': 'product key is null, list expected'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(req_data.get('products'), str):
            return Response({'error': 'product key is str, list expected'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(req_data.get('products'), list) and not req_data.get('products'):
            return Response({'error': 'product list is empty'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(req_data.get('products'), list):
            return Response({'error': 'product key is not list'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(address=req_data.get('address'),
                             name=req_data.get('firstname'),
                             surname=req_data.get('lastname'),
                             cellphone_number=req_data.get('phonenumber'))
        for order_item in req_data.get('products'):
            OrderItem.objects.create(quantity=order_item.get('quantity'),
                                     order=order,
                                     product_id=order_item.get('product'))

        return Response({'status': 'Order has been created'})

    except ValueError:
        return JsonResponse({
            'error': 'Can not load json!',
        }, status=status.HTTP_400_BAD_REQUEST)


