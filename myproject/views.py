from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, F, Sum
from django.db import IntegrityError, transaction
from myproject.models import Product, Customer, Order, CartItem

# Категорії для генерації підказок
CATEGORY_PROMPTS = {
    "смартфони": {
        "desc": "Флагманський смартфон із передовими технологіями, чудовою камерою та високою продуктивністю.",
        "specs": "Екран: 6.7 OLED, Процесор: A17 Pro, Пам'ять: 256 ГБ"},
    "планшети": {"desc": "Потужний і компактний планшет для навчання, роботи, творчості та медіаконтенту.",
                 "specs": "Екран: 11 IPS, Процесор: Apple M2, Пам'ять: 128 ГБ"},
    "ноутбуки": {"desc": "Високопродуктивний ноутбук для програмування, складних робочих завдань та сучасних ігор.",
                 "specs": "Екран: 16 IPS, Процесор: Core i7, Відеокарта: RTX 4060, ОЗУ: 16 ГБ"},
    "комп'ютери": {"desc": "Потужний системний блок для геймінгу на ультра-налаштуваннях.",
                   "specs": "Ryzen 7 7800X3D, RTX 4070 Ti, ОЗУ: 32 ГБ DDR5, SSD: 2 ТБ"},
    "монітори": {"desc": "Ігровий монітор із високою частотою оновлення для максимальної плавності.",
                 "specs": "Діагональ: 27, Матриця: IPS, 2K, Частота: 144 Гц, 1 мс"},
    "відеокарти": {"desc": "Топова графічна карта для забезпечення максимального FPS у сучасних іграх.",
                   "specs": "Пам'ять: 16 ГБ GDDR6X, Шина: 256 біт, Інтерфейс: PCIe 4.0"}
}


# Декоратор для перевірки, чи вибрав користувач акаунт клієнта
def customer_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'customer_id' not in request.session:
            messages.warning(request, "🔒 Будь ласка, увійдіть у свій акаунт клієнта, щоб отримати доступ до магазину.")
            return redirect('login')
        return view_func(request, *args, **kwargs)

    return wrapper


# Супутні дані про клієнта та кількість товарів у кошику для передачі в контекст базового шаблону
def get_base_context(request):
    context = {}
    if 'customer_id' in request.session:
        customer = Customer.objects.filter(pk=request.session['customer_id']).first()
        if customer:
            context['current_customer'] = customer
            context['cart_count'] = CartItem.objects.filter(customer=customer).aggregate(total=Sum('quantity')).get(
                'total') or 0
    return context


@customer_login_required
def index(request):
    context = get_base_context(request)
    cat_filter = request.GET.get('category', '').strip().lower()
    search_query = request.GET.get('search', '').strip()

    products = Product.objects.all()
    if cat_filter:
        products = products.filter(category=cat_filter)
    if search_query:
        products = products.filter(name__icontains=search_query)

    sales_data = Order.objects.aggregate(total=Sum(F('product__price') * F('quantity')))
    total_sales = sales_data.get('total') or 0

    order_counts = Order.objects.count()
    avg_check = total_sales / order_counts if order_counts > 0 else 0

    popular_cat = Order.objects.values('product__category').annotate(count=Count('id')).order_by('-count').first()
    products_per_cat = Product.objects.values('category').annotate(count=Count('product_id'))

    # Створюємо список категорій з красивими іконками за замовчуванням
    icons_map = {"смартфони": "📱", "планшети": "📟", "ноутбуки": "💻", "комп'ютери": "🖥️", "монітори": "📺",
                 "відеокарти": "🔌"}
    categories_with_icons = []
    for item in products_per_cat:
        cat_name = item['category']
        categories_with_icons.append({
            'name': cat_name,
            'count': item['count'],
            'icon': icons_map.get(cat_name, "📦")
        })

    context.update({
        'products': products,
        'total_sales': round(total_sales, 2),
        'avg_check': round(avg_check, 2),
        'popular_cat': popular_cat,
        'categories': categories_with_icons,
        'selected_category': cat_filter,
        'search_query': search_query
    })
    return render(request, 'menu.html', context)


# --- Ситема логіну / Реєстрації через Сесії ---

def login_view(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')

        if customer_id:
            try:
                # Шукаємо клієнта в базі за його ID
                customer = Customer.objects.get(pk=customer_id)

                # Записуємо ID клієнта в сесію, щоб сайт "пам'ятав" його
                request.session['customer_id'] = customer.pk
                request.session['customer_name'] = f"{customer.first_name} {customer.last_name}"

                messages.success(request, f"Успішний вхід! Вітаємо, {customer.first_name}.")
                return redirect('menu')  # Перенаправляє на головну сторінку магазину
            except Customer.DoesNotExist:
                messages.error(request, "Помилка: такого клієнта не знайдено.")
        else:
            messages.error(request, "Будь ласка, оберіть профіль для входу.")

    # Якщо це GET-запит (просто відкрили сторінку), передаємо всіх клієнтів для випадаючого списку
    existing_customers = Customer.objects.all()
    return render(request, 'auth/login.html', {'existing_customers': existing_customers})
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if not first_name or not last_name or not email:
            messages.error(request, "❌ Заповніть усі поля!")
            return redirect('register')

        try:
            customer = Customer.objects.create(first_name=first_name, last_name=last_name, email=email)
            request.session['customer_id'] = customer.id
            messages.success(request, f"🎉 Акаунт успішно створено! Ласкаво просимо, {first_name}!")
            return redirect('menu')
        except IntegrityError:
            messages.error(request, "❌ Клієнт з таким Email вже існує в базі!")
            return redirect('register')

    return render(request, 'auth/register.html')


def logout_view(request):
    if 'customer_id' in request.session:
        del request.session['customer_id']
    messages.info(request, "🚪 Ви вийшли з акаунта.")
    return redirect('login')


# --- Логіка Багатотоварного Кошика ---

@customer_login_required
def cart_detail(request):
    context = get_base_context(request)
    customer = context['current_customer']
    cart_items = CartItem.objects.filter(customer=customer).select_related('product')

    total_cart_price = sum(item.total_price for item in cart_items)

    context.update({
        'cart_items': cart_items,
        'total_cart_price': round(total_cart_price, 2)
    })
    return render(request, 'cart.html', context)


@customer_login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    customer = get_object_or_404(Customer, pk=request.session['customer_id'])

    if product.stock <= 0:
        messages.error(request, f"❌ Товар '{product.name}' закінчився на складі!")
        return redirect('menu')

    cart_item, created = CartItem.objects.get_or_create(customer=customer, product=product)
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"🟣 Кількість '{product.name}' в кошику збільшено!")
        else:
            messages.warning(request, f"⚠️ Не можна додати більше. На складі є лише {product.stock} шт.")
    else:
        messages.success(request, f"🛒 '{product.name}' додано до кошика!")

    return redirect('menu')


@customer_login_required
def update_cart_quantity(request, item_id, action):
    cart_item = get_object_or_404(CartItem, pk=item_id, customer_id=request.session['customer_id'])
    if action == 'inc':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f"⚠️ Максимально доступно на складі: {cart_item.product.stock} шт.")
    elif action == 'dec':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, "🗑️ Товар видалено з кошика.")
    elif action == 'delete':
        cart_item.delete()
        messages.info(request, "🗑️ Товар видалено з кошика.")

    return redirect('cart_detail')


@customer_login_required
def checkout(request):
    customer = get_object_or_404(Customer, pk=request.session['customer_id'])
    cart_items = CartItem.objects.filter(customer=customer).select_related('product')

    if not cart_items.exists():
        messages.error(request, "❌ Ваш кошик порожній!")
        return redirect('menu')

    # Використовуємо транзакцію бази даних, щоб якщо один товар зламається, все замовлення скасувалося
    with transaction.atomic():
        for item in cart_items:
            product = item.product
            if product.stock < item.quantity:
                messages.error(request,
                               f"❌ Помилка: На складі залишилось всього {product.stock} шт. товару '{product.name}'!")
                return redirect('cart_detail')

            # Створюємо офіційне замовлення
            Order.objects.create(customer=customer, product=product, quantity=item.quantity)

            # Зменшуємо залишок на складі
            product.stock -= item.quantity
            product.save()

        # Очищуємо кошик після успішного оформлення
        cart_items.delete()

    messages.success(request, "🎉 Замовлення успішно оформлено для всіх товарів! Дякуємо за покупку!")
    return redirect('menu')


# --- Інші стандартні функції, адаптовані під дизайн ---

@customer_login_required
def product_detail(request, pk):
    context = get_base_context(request)
    product = get_object_or_404(Product, pk=pk)
    context['product'] = product
    return render(request, 'product_detail.html', context)


@customer_login_required
def add_product(request):
    context = get_base_context(request)
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category', '').strip().lower()
        price = float(request.POST.get('price', 0))
        stock = int(request.POST.get('stock', 0))
        description = request.POST.get('description')
        specs = request.POST.get('specs')

        Product.objects.create(name=name, category=category, price=price, stock=stock, description=description,
                               specs=specs)
        messages.success(request, "✅ Новий гаджет успішно додано до каталогу!")
        return redirect('menu')

    context['prompts'] = CATEGORY_PROMPTS
    return render(request, 'add_product.html', context)


@customer_login_required
def edit_product(request, pk):
    context = get_base_context(request)
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name') or product.name
        product.price = float(request.POST.get('price') or product.price)
        product.stock = int(request.POST.get('stock') or product.stock)
        product.description = request.POST.get('description') or product.description
        product.specs = request.POST.get('specs') or product.specs
        product.save()
        messages.success(request, "✅ Дані товару успішно оновлено!")
        return redirect('menu')
    context['product'] = product
    return render(request, 'edit_product.html', context)


@customer_login_required
def show_customers(request):
    context = get_base_context(request)
    customers_list = Customer.objects.all()
    customers_data = []
    for c in customers_list:
        count = Order.objects.filter(customer=c).count()
        customers_data.append({'customer': c, 'order_count': count})
    context['customers_data'] = customers_data
    return render(request, 'customers.html', context)


@customer_login_required
def show_orders(request):
    context = get_base_context(request)
    orders = Order.objects.all().select_related('customer', 'product').order_by('-order_date')
    for order in orders:
        order.total_price = order.product.price * order.quantity
    context['orders'] = orders
    return render(request, 'orders.html', context)


@customer_login_required
def update_prices(request):
    if request.method == 'POST':
        percentage = float(request.POST.get('percentage', 0))
        Product.objects.update(price=F('price') * (1 + percentage / 100.0))
        messages.success(request, f"📈 Ціни по всьому каталогу підвищено на {percentage}%!")
    return redirect('menu')


@customer_login_required
def decrease_prices(request):
    if request.method == 'POST':
        percentage = float(request.POST.get('percentage', 0))
        Product.objects.update(price=F('price') * (1 - percentage / 100.0))
        messages.success(request, f"📉 Масова знижка діє! Ціни знижено на {percentage}%!")
    return redirect('menu')


@customer_login_required
def delete_item(request, item_type, pk):
    if item_type == 'product':
        get_object_or_404(Product, pk=pk).delete()
    elif item_type == 'customer':
        get_object_or_404(Customer, pk=pk).delete()
    elif item_type == 'order':
        get_object_or_404(Order, pk=pk).delete()
    messages.success(request, "🗑️ Запис назавжди видалено з системи.")
    return redirect('menu')


@customer_login_required
def clear_table(request, table_name):
    if table_name == 'products':
        Product.objects.all().delete()
    elif table_name == 'customers':
        Customer.objects.all().delete()
    elif table_name == 'orders':
        Order.objects.all().delete()
    messages.success(request, f"🗑️ Усі записи з таблиці {table_name} успішно видалено.")
    return redirect('menu')