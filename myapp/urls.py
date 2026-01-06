from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import UserLoginForm

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=UserLoginForm), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),

    # Shop & Cart
    path('', views.shop, name='shop'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # Custom Admin
    path('custom-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/add/', views.add_product, name='add_product'),
    path('custom-admin/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('custom-admin/delete/<int:pk>/', views.delete_product, name='delete_product'),
]
