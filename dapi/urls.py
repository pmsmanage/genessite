from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UpdateUserView, ChangePasswordView, ActiveUserView, CreateProductView,\
    UpdateProductView, CreateOrderView, UpdateOrderView, CreateDNAScopingServiceView, UsersListView, UserView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='user-register'),
    path('update_profile/<int:pk>/', UpdateUserView.as_view(), name='update-profile'),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='change-password'),
    path('activate/<int:pk>/', ActiveUserView.as_view(), name='activate-user'),
    path('products/', CreateProductView.as_view(), name='add-product'),
    path('products/<int:pk>/', UpdateProductView.as_view(), name='update-product'),
    path('orders/', CreateOrderView.as_view(), name='add-order'),
    path('orders/<int:pk>/', UpdateOrderView.as_view(), name='update-order'),
    path('services/', CreateDNAScopingServiceView.as_view(), name='add-service'),
    path('users/', UsersListView.as_view(), name='users_list'),
    path('users/<int:pk>/', UserView.as_view(), name='view-user'),
]
