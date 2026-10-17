from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart-detail'),
    path('add/', views.add_to_cart, name='cart-add'),
    path('edit/', views.edit_cart, name='cart-edit'),
    path('delete/<int:item_id>/', views.remove_cart_item, name='cart-delete'),
]
