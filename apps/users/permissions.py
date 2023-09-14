from rest_framework import permissions
from rest_framework.permissions import BasePermission


class AnonPermission(permissions.BasePermission):
    message = 'You are already authenticated'

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAuthenticatedOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            # Уже авторизованный пользователь
            return True
        else:
            # Неавторизованный пользователь. Вы можете добавить свою логику здесь.
            # Например, вернуть False, если вы хотите запретить доступ неавторизованным пользователям
            # или выполнить другие проверки по вашим требованиям.
            return False


class IsSellerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            return request.user.is_seller

        if request.method == 'GET' and request.user.is_authenticated and not request.user.is_seller:
            return True

        return False


class IsProductOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Проверка, является ли текущий пользователь владельцем продукта
        return obj.seller == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """Класс разрешений для владельца объекта"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.creator == request.user


class IsProductOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            if request.user.is_superuser:
                return True
            return obj.seller == request.user
        return True


class IsProductOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            if request.user.is_superuser:
                return True
            return obj.seller == request.user
        return True


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.method in ['GET', 'HEAD', 'OPTIONS']
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.method in ['GET', 'HEAD', 'OPTIONS']