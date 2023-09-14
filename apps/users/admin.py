from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, Profile


class MyUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'is_seller']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_seller']
    search_fields = ['email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'patronymic', 'phone_number', 'description')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_seller')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'is_seller'),
        }),
    )
    ordering = ['email']
    filter_horizontal = []


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Profile)
