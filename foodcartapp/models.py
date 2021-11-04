from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum, F


class RestaurantQuerySet(models.QuerySet):
    def available(self, order_id):
        order_product_ids = list(OrderItem.objects.values_list('product', flat=True).filter(order_id=order_id))
        restaurant_menu = list(RestaurantMenuItem.objects.filter(product__in=order_product_ids, availability=True))
        burger_restaurant_ids = [
            {rest_item.restaurant.id for rest_item in restaurant_menu if product_id == rest_item.product_id} for
            product_id in order_product_ids]
        total_restaurant_ids = set.intersection(*burger_restaurant_ids)
        return Restaurant.objects.filter(id__in=total_restaurant_ids)


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    restaurants = RestaurantQuerySet.as_manager()
    objects = models.Manager()

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class OrderQuerySet(models.QuerySet):
    def unprocessed(self):
        return self.filter(status='N')

    def with_price(self):
        return self.annotate(cost=Sum(F('order_items__cost')))


class Order(models.Model):
    STATUSES = (
        ('N', 'Необработанный'),
        ('C', 'Выполненный'),
    )
    PAYMENT = (
        ('C', 'Наличностью'),
        ('E', 'Электронно'),
    )

    status = models.CharField(max_length=2, choices=STATUSES, default='N', db_index=True)
    payment_method = models.CharField(max_length=2, choices=PAYMENT, null=True, blank=True, db_index=True)

    address = models.CharField('адрес', max_length=255)
    firstname = models.CharField('имя', max_length=255)
    lastname = models.CharField('фамилия', max_length=255)
    phonenumber = PhoneNumberField('мобильный телефон', db_index=True)
    comment = models.TextField('комментарий', blank=True)

    registered_at = models.DateTimeField('зарегистрирован', auto_now_add=True, db_index=True)
    called_at = models.DateTimeField('позвонить', blank=True, null=True, db_index=True)
    delivered_at = models.DateTimeField('доставлен', blank=True, null=True, db_index=True)

    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    orders = OrderQuerySet.as_manager()
    objects = models.Manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.address}"


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=512,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='order_items',
        verbose_name="заказ",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    quantity = models.IntegerField(
        'количество',
        validators=[MinValueValidator(1)])
    cost = models.DecimalField(
        'стоимость',
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f"{self.order.address} - {self.product.name}"

