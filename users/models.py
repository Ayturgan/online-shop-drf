from django.db.models import *
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .manager import CustomUserManager


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = None
    email = EmailField('email address', unique=True)
    password = CharField(max_length=255, null=False, blank=False)

    first_name = CharField(max_length=255, null=False, blank=False)
    last_name = CharField(max_length=255, null=False, blank=False)
    patronymic = CharField(max_length=255, null=True, blank=False)
    phone_number = IntegerField(null=True)
    description = CharField(max_length=255, null=True, blank=True)

    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    is_seller = BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'


class Notice(Model):
    user = ForeignKey(MyUser, on_delete=CASCADE)
    message = TextField(null=True)
    is_approved = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Request from {self.user.email}'


class Profile(Model):
    user = OneToOneField(MyUser, on_delete=CASCADE)
    date_of_birth = DateField(blank=True, null=True)
    photo = ImageField(upload_to='photo/', blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.email)

