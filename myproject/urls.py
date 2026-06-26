from django.urls import path
from myproject import views

urlpatterns = [
    path('', views.index, name='menu'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('customers/', views.show_customers, name='show_customers'),
    path('orders/', views.show_orders, name='show_orders'),
    path('update_prices/', views.update_prices, name='update_prices'),
    path('decrease_prices/', views.decrease_prices, name='decrease_prices'),
    path('delete/<str:item_type>/<int:pk>/', views.delete_item, name='delete_item'),
    path('clear/<str:table_name>/', views.clear_table, name='clear_table'),

    # Нові маршрути для Акаунтів та Кошика
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/checkout/', views.checkout, name='checkout'),
]