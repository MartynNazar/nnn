from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Product, CartItem


# 1. Головна сторінка (Тільки після входу)
@login_required(login_url='login')
def index(request):
    products = Product.objects.all()

    # Перевіряємо, чи це адмін
    is_admin = request.user.is_staff

    # Отримуємо унікальний кошик поточного користувача з бази даних
    cart_items = CartItem.objects.filter(user=request.user)

    context = {
        'products': products,
        'is_admin': is_admin,
        'cart_items': cart_items,
        'username': request.user.username
    }
    return render(request, 'menu.html', context)


# 2. Функціонал адміна: Зміна ціни прямо в базі
@login_required
def update_price(request, product_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Немає прав адміна'}, status=403)

    if request.method == 'POST':
        new_price = request.POST.get('price')
        product = get_object_or_404(Product, product_id=product_id)
        product.price = new_price
        product.save()
        return redirect('index')


# 3. Унікальний кошик: додавання
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('index')


# 4. API для автопідстановки користувачів (AJAX)
@login_required
def suggest_customers(request):
    q = request.GET.get('q', '')
    if q:
        # Шукаємо користувачів, чиє ім'я починається з введених літер
        users = User.objects.filter(username__icontains=q)[:5]
        results = [{'username': u.username, 'email': u.email} for u in users]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)