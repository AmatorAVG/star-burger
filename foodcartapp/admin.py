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
    ]

    list_filter = ['payment_method']

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

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            request.id_for_formfield = obj.id
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "restaurant":

            kwargs["queryset"] = Restaurant.restaurants.available(request.id_for_formfield)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            if url_has_allowed_host_and_scheme(request.GET['next'], None):
                return HttpResponseRedirect(request.GET['next'])
            return HttpResponseRedirect(reverse('start_page'))
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
