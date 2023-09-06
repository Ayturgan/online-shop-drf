from django.db.models import Avg, Sum
from django.urls import reverse
from rest_framework.serializers import *
from .models import Product, Category, Review, CartItem, Cart
from users.models import MyUser


class UserSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email',)


class ReviewSerializer(ModelSerializer):
    creator = UserSerializer(read_only=True)
    product_id = CharField(read_only=False)

    class Meta:
        model = Review
        fields = ('id', 'creator', 'product_id', 'text', 'rating', 'created_at', 'updated_at',)

    def create(self, validated_data):
        user = self.context["request"].user
        product_id = validated_data.get("product_id")
        existing_reviews = Review.objects.filter(creator=user, product_id=product_id)
        if existing_reviews.exists():
            raise ValidationError("User has already left a review for this product")

        validated_data["creator"] = user
        return super().create(validated_data)


class ProductCreateSerializer(ModelSerializer):
    seller = HiddenField(default=CurrentUserDefault())
    views = HiddenField(default=0)

    class Meta:
        model = Product
        fields = '__all__'


class SellerSerializer(ModelSerializer):
    profile = HyperlinkedRelatedField(
        view_name='users:profile-id',
        lookup_field='id',
        read_only=True,
    )

    class Meta:
        model = MyUser
        fields = ('profile',)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class ReviewRatingSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = ('text', )


class ProductSerializer(ModelSerializer):
    seller = SerializerMethodField()
    category = CategorySerializer()
    reviews = SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_seller(self, obj):
        seller = obj.seller
        if seller:
            host = "http://127.0.0.1:8000/"
            profile_url = f"{host}accounts/profile/{seller.id}/"
            return {'profile': profile_url}
        return None

    def get_reviews(self, obj):
        reviews = Review.objects.filter(product=obj)
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

        review_data = ReviewRatingSerializer(reviews, many=True).data
        return {"reviews": review_data, "average_rating": average_rating}

    def to_representation(self, instance):
        # Увеличиваем количество просмотров продукта на 1
        instance.views += 1
        instance.save()

        return super().to_representation(instance)


class ProductUpdateSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'slug', 'image', 'description', 'category', 'price', 'stock', 'available')


class CategoryListSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductAnalyticsSerializer(Serializer):
    total_views = IntegerField()
    total_reviews = IntegerField()
    average_product_rating = FloatField()


class CartItemSerializer(ModelSerializer):

    class Meta:
        model = CartItem
        fields = ('quantity', )


class PaymentSerializer(Serializer):
    total = DecimalField(max_digits=10, decimal_places=2)
    currency = CharField()


class ProductItemSerializer(Serializer):
    id = IntegerField(source='product.id')
    quantity = IntegerField()


class CartDetailSerializer(Serializer):
    cart_id = IntegerField(source='id')
    products = ProductItemSerializer(many=True, source='items')
    payment = PaymentSerializer()

    def to_representation(self, instance):
        items = instance.items.all()
        total = sum(item.total_price for item in items)
        currency = "USD"

        data = {
            "cart_id": instance.id,
            "products": ProductItemSerializer(items, many=True).data,
            "payment": {
                "total": total,
                "currency": currency,
            },
        }
        return data



