from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('categories/add', CategoryAddAPIView.as_view(), name='category-add'),

    path('product-analytics/<int:id>/', ProductAnalyticsAPIView.as_view(), name='product-analytics'),
    path('products/<int:id>/add-product/', CartItemAddProductAPIView.as_view(), name='add-product-to-cart'),

    path('cart/remove-product/<int:id>/', CartItemRemoveAPIView.as_view(), name='remove-product-from-cart'),

    path('cart/checkout/', CreateCheckoutSession.as_view()),

    path('cart/', CartDetailView.as_view(), name='cart-list'),

    path('cart/checkout/success/', CheckoutSuccessView.as_view(), name='checkout-success'),
    path('cart/checkout/failed/', CheckoutFailedView.as_view(), name='checkout-failed'),
]
