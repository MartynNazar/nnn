from django.contrib import admin
from django.urls import path
from myproject import views

urlpatterns = [
    path('admin-panel/', admin.site.urls),  # Стандартна адмінка Django для суперюзера

    # Авторизація
    path('login/', views.customer_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),

    # Головна та товари
    path('', views.index, name='menu'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete/<str:item_type>/<int:pk>/', views.delete_item, name='delete_item'),
    path('clear/<str:table_name>/', views.clear_table, name='clear_table'),

    # Клієнти
    path('customer/add/', views.add_customer, name='add_customer'),
    path('customers/', views.show_customers, name='show_customers'),

    # Кошик (Cart)
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),

    # Замовлення та Керування цінами
    path('orders/', views.show_orders, name='show_orders'),
    path('prices/increase/', views.update_prices, name='update_prices'),
    path('prices/decrease/', views.decrease_prices, name='decrease_prices'),

    # Відгуки
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
]