import secrets

import requests
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework.serializers import *
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.product.models import Cart
from .models import MyUser, Notice, Profile


# REGISTER AND AUTHENTICATE
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['email'] = user.email
        token['is_seller'] = user.is_seller
        return token


class RegisterUserSerializer(ModelSerializer):
    email = EmailField(
        required=True,
        validators=[UniqueValidator(queryset=MyUser.objects.all())]
    )

    password = CharField(write_only=True, required=True, validators=[validate_password])
    password2 = CharField(write_only=True, required=True)

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password": "Password fields didn't match."})
        email = attrs['email']
        url = f"https://api.emailhunter.co/v2/email-verifier?email={email}&api_key=51590a7516dd4855a2192a6ed4018e757006cc67"
        response = requests.get(url)
        data = response.json()
        email_verify = data["data"]["status"]
        if email_verify == "invalid":
            raise ValidationError("Email doesn't exist")
        return attrs

    # def send_confirmation_email(self, email, confirmation_code):
    #     subject = 'Подтверждение адреса электронной почты'
    #     message = f'Ваш код подтверждения: {confirmation_code}'
    #     from_email = 'ayturgankgs@gmail.com'
    #     recipient_list = [email]
    #
    #     send_mail(subject, message, from_email, recipient_list)

    def create(self, validated_data):
        user = MyUser.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        # confirmation_code = secrets.token_hex(16)
        # self.send_confirmation_email(user.email, confirmation_code)

        Cart.objects.create(user=user)
        Profile.objects.create(user=user)

        return user


# profile and current-profile
class GetUserDataSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email', 'first_name', 'last_name', 'patronymic', 'phone_number', 'description', 'is_seller')


class CurrentProfileSerializer(ModelSerializer):
    user = GetUserDataSerializer()

    class Meta:
        model = Profile
        fields = ('user', 'date_of_birth', 'photo', )

    def get_user(self, obj):
        user = obj.user
        user_data = GetUserDataSerializer(user).data
        return user_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request') and self.context['request'].method == 'PUT':
            self.fields['user'].fields.pop('email')
            self.fields['user'].fields.pop('is_seller')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        for attr, value in user_data.items():
            setattr(user, attr, value)

        user.save()

        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.photo = validated_data.get('photo', instance.photo)

        instance.save()

        return instance


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email', 'first_name', 'last_name', 'patronymic', 'phone_number', 'description', 'is_seller')


# USERS LIST
class UsersListSerializer(ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email', 'first_name', 'last_name', 'patronymic', 'phone_number', 'description', 'is_seller')


# USER TO BECOME SELLER AND ADMIN APPROVE
class UserSellerBecomeSerializer(Serializer):
    choice = BooleanField(
        required=True,
        label='Do you want to be a seller?'
    )

    def validate_choice(self, value):
        if not isinstance(value, bool):
            raise ValidationError('Unacceptable choice.')
        return value


class NoticeSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = Notice
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.email


class AdminApproveSellerSerializer(ModelSerializer):
    class Meta:
        model = Notice
        fields = ('user', 'message', 'is_approved', 'created_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'PUT':
            for field_name in ('message', 'created_at'):
                self.fields.pop(field_name, None)


