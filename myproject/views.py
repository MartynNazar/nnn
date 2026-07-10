from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Customer, Product, CartItem


def index(request):
    # ТЕПЕР СЮДИ МОЖЕ ЗАЙТИ БУДЬ-ХТО (БЕЗ ОБОВ'ЯЗКОВОГО ЛОГІНУ)
    products = Product.objects.all()

    # Кошик підвантажуємо тільки якщо користувач увійшов
    cart_items = []
    username = None
    is_admin = False

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        username = request.user.username
        is_admin = request.user.is_staff

    context = {
        'products': products,
        'cart_items': cart_items,
        'username': username,
        'is_admin': is_admin,
    }
    return render(request, 'menu.html', context)


def customer_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        action = request.POST.get('action')  # Перевіряємо: login чи register

        # --- ЛОГІКА РЕЄСТРАЦІЇ ---
        if action == 'register':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Користувач з таким Email вже існує!")
                return render(request, 'login.html', {'active_tab': 'register'})

            username = email.split('@')[0]
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
            Customer.objects.create(user=user, phone=phone, address=address)

            messages.success(request, "Реєстрація успішна! Тепер увійдіть.")
            return render(request, 'login.html', {'active_tab': 'login'})

        # --- ЛОГІКА ВХОДУ ---
        else:
            role = request.POST.get('role', 'client')

            if role == 'admin':
                username = request.POST.get('username')
                password = request.POST.get('password')

                if username == 'admin' and password == '2011':
                    user, created = User.objects.get_or_create(username='admin',
                                                               defaults={'is_staff': True, 'is_superuser': True})
                    if created:
                        user.set_password('2011')
                        user.save()

                    auth_user = authenticate(username='admin', password='2011')
                    if auth_user:
                        auth_login(request, auth_user)
                        return redirect('index')

                messages.error(request, "Неправильний логін або пароль адміна!")

            else:  # Вхід для клієнта (Email + Ім'я та Прізвище)
                email = request.POST.get('username')
                fullname = request.POST.get('password')

                try:
                    user = User.objects.get(email=email)
                    user_fullname = f"{user.first_name} {user.last_name}".strip()

                    if fullname.lower() == user_fullname.lower():
                        auth_login(request, user)
                        return redirect('index')
                    else:
                        messages.error(request, "Прізвище та Ім'я не збігаються!")
                except User.DoesNotExist:
                    messages.error(request, "Користувача з такою поштою не знайдено!")

    return render(request, 'login.html', {'active_tab': 'login'})


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


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('index')