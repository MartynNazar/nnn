from django.contrib import admin
from django.urls import path
from myproject import views

urlpatterns = [
    # Головна сторінка сайту
    path('', views.index, name='index'),


    path('login/', views.customer_login, name='login'),


    path('update-price/<int:product_id>/', views.update_price, name='update_price'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Адмінка
    path('admin/', admin.site.urls),
]