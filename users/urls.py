from django.contrib.auth import views
from django.urls import path
from .views import AdminApproveSellerView, UsersListAPIView, LoginView, RegisterUserAPIView, CurrentProfileAPIView, \
    ProfileAPIView, UserToBecomeSellerView


urlpatterns = [
    path('admin/notice/', AdminApproveSellerView.as_view(), name='admin-notice'),
    path('admin/accounts/list/', UsersListAPIView.as_view(), name='users-list'),

    path('login_token/', LoginView.as_view(), name='get-token'),
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    # path('register/confirm/', ConfirmEmailAPIView.as_view(), name='register'),

    path('accounts/profile/', CurrentProfileAPIView.as_view(), name='current-profile'),
    path('accounts/profile/<int:id>/', ProfileAPIView.as_view(), name='profile-id'),

    path('seller/become/', UserToBecomeSellerView.as_view(), name='seller-become'),

]
