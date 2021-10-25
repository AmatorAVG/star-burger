from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import Order
from .models import RestaurantMenuItem
from .models import OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'firstname',
        'lastname',
        'address',
        'phonenumber',
        'comment',
        'payment_method',
    ]
    list_display = [
        'firstname',
        'lastname',
        'address',
        'phonenumber',
        'status',
        'comment',
        'registered_at',
        'called_at',
        'delivered_at',
        'payment_method',
        'restaurant',
    ]
    inlines = [
        OrderItemInline
    ]

    readonly_fields = ('registered_at',)

    my_id_for_formfield = None

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.my_id_for_formfield = obj.id
        return super(OrderAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "restaurant":

            order_products = list(OrderItem.objects.values_list('product', flat=True).filter(order_id=self.my_id_for_formfield))
            restaurant_menu = list(RestaurantMenuItem.objects.filter(product__in=order_products, availability=True))
            burger_restaurants = [{rest_item.restaurant.id for rest_item in restaurant_menu if product == rest_item.product_id} for product in order_products]

            if len(burger_restaurants):
                total_restaurants = burger_restaurants[0]
                for burger_restaurant in burger_restaurants:
                    total_restaurants &= burger_restaurant
            else:
                total_restaurants = set()
            kwargs["queryset"] = Restaurant.objects.filter(id__in=total_restaurants)

        return super(OrderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            if url_has_allowed_host_and_scheme(request.GET['next'], None):
                return HttpResponseRedirect(request.GET['next'])
            raise
        return res


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass
