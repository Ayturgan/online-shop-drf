from django.db.models import *
from apps.users.models import *


class Category(Model):
    name = CharField(max_length=200, db_index=True)
    slug = SlugField(max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(Model):
    seller = ForeignKey(MyUser, on_delete=CASCADE)
    category = ForeignKey(Category, related_name='products', on_delete=CASCADE)
    name = CharField(max_length=200, db_index=True)
    slug = SlugField(max_length=200, db_index=True)
    image = ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = TextField(blank=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    stock = PositiveIntegerField()
    available = BooleanField(default=True)
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    views = PositiveIntegerField(default=0)


    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name


class Review(Model):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    RATING = [(ONE, 1), (TWO, 2), (THREE, 3), (FOUR, 4), (FIVE, 5), ]
    creator = ForeignKey(
        MyUser,
        on_delete=CASCADE,
    )
    product = ForeignKey(Product, on_delete=CASCADE)
    text = TextField(default='')
    rating = IntegerField(
        choices=RATING,
        default=FIVE
    )
    created_at = DateTimeField(
        auto_now_add=True
    )
    updated_at = DateTimeField(
        auto_now=True
    )


class Cart(Model):
    user = ForeignKey(MyUser, on_delete=CASCADE, related_name='cart')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class CartItem(Model):
    cart = ForeignKey(Cart, on_delete=CASCADE, related_name='items')
    product = ForeignKey(Product, on_delete=CASCADE)
    quantity = PositiveIntegerField(default=1)
    total_price = DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Пересчитываем сумму товаров в корзине при сохранении
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)



