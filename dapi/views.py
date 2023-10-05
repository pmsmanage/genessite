from rest_framework import generics
from django.contrib.auth.models import User

from .serializers import RegisterSerializer, UpdateUserSerializer, ChangePasswordSerializer,\
    ActivateUserSerializer, CreateUpdateProductSerializer, CreateOrderSerializer, UpdateOrderSerializer, \
    CreateDNAScoringServiceSerializer, UserDetailSerializer
from .models import Product, Order, DNAService
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser, IsSuperUserOrOwner
# Create your views here.


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RegisterSerializer


class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer


class ActiveUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ActivateUserSerializer


class CreateProductView(generics.CreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUpdateProductSerializer


class UpdateProductView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CreateUpdateProductSerializer


class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CreateOrderSerializer


class UpdateOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateOrderSerializer


class CreateDNAScopingServiceView(generics.CreateAPIView):
    queryset = DNAService.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CreateDNAScoringServiceSerializer


class UsersListView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSuperUser]
    serializer_class = UserDetailSerializer


class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSuperUserOrOwner]
    serializer_class = UserDetailSerializer
