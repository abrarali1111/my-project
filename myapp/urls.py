from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import UserLoginForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=UserLoginForm), name='login'),
    # Changed to use the custom_logout view
    path('logout/', views.custom_logout, name='logout'),
    path('', views.item_list, name='item_list'),
    path('item/add/', views.item_create, name='item_add'),
    path('item/<int:pk>/edit/', views.item_update, name='item_edit'),
    path('item/<int:pk>/delete/', views.item_delete, name='item_delete'),
]
