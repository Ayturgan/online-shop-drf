from rest_framework.generics import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
import stripe

from online_shop import settings
from .serializers import *
from .models import *
from users.permissions import IsOwnerOrAdmin, IsProductOwnerOrReadOnly, IsAdminOrReadOnly, IsSellerOrReadOnly, \
    IsProductOwnerOrAdminOrReadOnly

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsSellerOrReadOnly, IsProductOwnerOrAdminOrReadOnly]

    filter_backends = [SearchFilter]
    search_fields = ['price', 'slug', 'category__slug']

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ProductSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProductUpdateSerializer
        else:
            return ProductCreateSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrAdmin()]
        return []


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryListSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['slug']


class CategoryAddAPIView(CreateAPIView):
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = CategoryListSerializer


class ProductAnalyticsAPIView(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Подсчитайте общее количество отзывов для данного продукта
        total_reviews = Review.objects.filter(product=product).count()

        # Вычислите среднюю оценку для данного продукта
        average_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

        total_views = product.views

        # Сериализуйте данные
        data = {
            'total_reviews': total_reviews,
            'total_views': total_views,
            'average_product_rating': average_rating,
        }

        serializer = ProductAnalyticsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartDetailSerializer

    def get_object(self):
        return Cart.objects.filter(user=self.request.user).first()


class CartItemAddProductAPIView(CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, id, *args, **kwargs):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        product = get_object_or_404(Product, id=id)
        quantity = int(request.data.get('quantity', 1))  # Получите значение quantity из запроса

        # Попробуйте найти элемент для данного продукта в корзине
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item:
            # Элемент уже существует, увеличьте его количество на указанное значение
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # Элемент не существует, создайте новый элемент с указанным количеством
            cart_item = CartItem(cart=cart, product=product, quantity=quantity)
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemRemoveAPIView(DestroyAPIView):
    queryset = CartItem.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        try:
            cart_item = self.get_object()
            cart_item.delete()
            return Response({"detail": "Product removed from cart."}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "Product not found in cart."}, status=status.HTTP_404_NOT_FOUND)


class CheckoutSuccessView(APIView):
    def get(self, request):
        message = "Оплата прошла успешно"
        return Response({"detail": message}, status=status.HTTP_200_OK)


class CheckoutFailedView(APIView):
    def get(self, request):
        message = "Оплата отменена или не удалась"
        return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)


def get_cart_items(user):
    cart_items = CartItem.objects.filter(user=user)
    return cart_items


class DummySerializer(serializers.Serializer):
    pass


class CreateCheckoutSession(CreateAPIView):
    serializer_class = DummySerializer

    def create(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(cart__user=request.user)

        line_items = []
        for item in cart_items:
            line_item = {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            }
            line_items.append(line_item)

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(reverse('checkout-success')),
                cancel_url=request.build_absolute_uri(reverse('checkout-failed')),
            )
            cart_items.delete()
            return Response({'session_url': checkout_session.url})
        except Exception as e:
            print(e)
            return Response({'error': 'Failed to create checkout session'}, status=500)



