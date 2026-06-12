from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='menu'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customer/list/', views.show_customers, name='show_customers'),
    path('order/new/', views.create_order, name='create_order'),
    path('order/list/', views.show_orders, name='show_orders'),
    path('prices/increase/', views.update_prices, name='update_prices'),
    path('prices/decrease/', views.decrease_prices, name='decrease_prices'),
    path('delete/<str:item_type>/<int:pk>/', views.delete_item, name='delete_item'),
    path('clear/<str:table_name>/', views.clear_table, name='clear_table'),
]