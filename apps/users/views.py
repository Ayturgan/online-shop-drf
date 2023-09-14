
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import status

import stripe

from online_shop import settings
from apps.product.models import Review
from apps.product.serializers import ReviewSerializer
from .serializers import *
from .models import *
from .permissions import *

stripe.api_key = settings.STRIPE_SECRET_KEY


# REGISTER AND AUTHENTICATE
class LoginView(TokenObtainPairView):
    permission_classes = (AnonPermission,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterUserAPIView(CreateAPIView):
    queryset = MyUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer


# PROFILE AND CURRENT-PROFILE
class CurrentProfileAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = CurrentProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        user = self.request.user
        print(f'user: {user}')
        return Profile.objects.get(user=user)


class ProfileAPIView(RetrieveAPIView, DestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAdminOrReadOnly, AllowAny]

    def get_object(self):
        user_id = self.kwargs.get('id')

        try:
            user = MyUser.objects.get(id=user_id)
            return user
        except MyUser.DoesNotExist:
            raise Http404


# USERS LIST
class UsersListAPIView(ListAPIView):
    queryset = MyUser.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = UsersListSerializer


# USER TO BECOME SELLER AND ADMIN APPROVE
class UserToBecomeSellerView(RetrieveAPIView):
    serializer_class = UserSellerBecomeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return None

    def post(self, request):
        user = request.user
        if user.is_seller:
            return Response({'message': 'You are already a seller.'}, status=status.HTTP_400_BAD_REQUEST)

        existing_request = Notice.objects.filter(user=user, is_approved=False).first()
        if existing_request:
            return Response({'message': 'The request to become a seller has already been sent and is pending.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSellerBecomeSerializer(data=request.data)
        if serializer.is_valid():
            choice = serializer.validated_data['choice']

            if choice:
                notice = Notice.objects.create(user=user, message='Wants to be a seller.')
                return Response({'message': 'Your request has been sent to the administrators for review.'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You declined a request to become a seller.'},
                                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminApproveSellerView(RetrieveUpdateAPIView):
    queryset = Notice.objects.all()
    serializer_class = AdminApproveSellerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        return None

    def get(self, request):
        notices = Notice.objects.all()
        serializer = NoticeSerializer(notices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        serializer = AdminApproveSellerSerializer(data=request.data)
        if serializer.is_valid():
            user_email = serializer.validated_data['user']
            is_approved = serializer.validated_data['is_approved']
            user = MyUser.objects.get(email=user_email)
            if is_approved:
                user.is_seller = True
                user.save()
                notice = Notice.objects.filter(user=user).first()
                if notice:
                    notice.delete()
            return Response({'message': 'Request successfully processed.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

