from django.contrib import admin
from django.urls import path, include
from myproject import views

urlpatterns = [
    # Головна сторінка
    path('', views.index, name='index'),

    # Стандартна авторизація Django (вона сама обробить URL /accounts/login/)
    path('accounts/', include('django.contrib.auth.urls')),

    # Твої інші шляхи (перевір, щоб назви функцій у views збігалися)
    path('update-price/<int:product_id>/', views.update_price, name='update_price'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Адмінка
    path('admin/', admin.site.urls),
]