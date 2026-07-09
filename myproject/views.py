from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, F
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from myproject.models import Product, Customer, Order, Review

# 25 категорій з унікальними підказками для адмінки
CATEGORY_PROMPTS = {
    "смартфони": {"desc": "Флагманський смартфон із передовими технологіями.",
                  "specs": "Екран: 6.7 OLED, Процесор: A17 Pro, Пам'ять: 256 ГБ"},
    "планшети": {"desc": "Потужний і компактний планшет для навчання та творчості.",
                 "specs": "Екран: 11 IPS, Процесор: M2, Пам'ять: 128 ГБ"},
    "ноутбуки": {"desc": "Високопродуктивний ноутбук для програмування та ігор.",
                 "specs": "Екран: 16 IPS 165Гц, Процесор: i7, RTX 4060, ОЗУ: 16 ГБ"},
    "комп'ютери": {"desc": "Потужний системний блок для геймінгу на ультра-налаштуваннях.",
                   "specs": "Ryzen 7 7800X3D, RTX 4070 Ti, ОЗУ: 32 ГБ DDR5"},
    "монітори": {"desc": "Ігровий монітор із високою частотою оновлення.",
                 "specs": "Діагональ: 27, Матриця: IPS, 2K, Частота: 144 Гц"},
    "телевізори": {"desc": "Сучасний телевізор із підтримкою Smart TV 4K.",
                   "specs": "Діагональ: 55, Neo QLED, Smart TV: ОС Tizen, 120 Гц"},
    "навушники": {"desc": "Бездротові навушники з активним шумозаглушенням.",
                  "specs": "Тип: Повнорозмірні, Бездротові, Шумозаглушення: ANC"},
    "колонки": {"desc": "Портативна бездротова акустична система із захистом від води.",
                "specs": "Потужність: 40 Вт, Захист: IP67, Акумулятор: 7500 мАг"},
    "годинники": {"desc": "Смарт-годинник преміум-класу для спорту та здоров'я.",
                  "specs": "Екран: 1.92 OLED, Корпус: Титан, Датчики: Пульсометр, ЕКГ"},
    "приставки": {"desc": "Ігрова консоль нового покоління для 4K геймінгу.",
                  "specs": "Процесор: AMD Zen 2, Графіка: RDNA 2, 825 ГБ SSD"},
    "ігри": {"desc": "Масштабна пригодницька гра з відкритим світом.",
             "specs": "Платформа: PS5, Жанр: RPG / Action, Локалізація: Українська"},
    "мишки": {"desc": "Бездротова кіберспортивна ігрова миша.",
              "specs": "Оптичний сенсор 30000 DPI, Вага: 63 г, Кнопки: 5"},
    "клавіатури": {"desc": "Механічна ігрова клавіатура з RGB підсвічуванням.",
                   "specs": "Тип: Механічна, Перемикачі: Red, Формат: TKL (80%)"},
    "відеокарти": {"desc": "Топова графічна карта для 4K геймінгу.",
                   "specs": "Пам'ять: 16 ГБ GDDR6X, Шина: 256 біт, Кулери: 3"},
    "процесори": {"desc": "Високопродуктивний багатоядерний процесор.",
                  "specs": "Сокет: AM5, Ядра: 8, Потоки: 16, Макс. частота: 5.0 ГГц"},
    "материнські плати": {"desc": "Надійна материнська плата з потужним живленням.",
                          "specs": "Чіпсет: AMD B650, Форм-фактор: ATX, Wi-Fi 6E"},
    "оперативна пам'ять": {"desc": "Швидкісний комплект пам'яті нового покоління.",
                           "specs": "Тип: DDR5, Об'єм: 32 ГБ (2x16), Частота: 6000 МГц"},
    "накопичувачі ssd": {"desc": "Надшвидкий внутрішній SSD накопичувач NVMe.",
                         "specs": "Об'єм: 1 ТБ, Швидкість читання: до 7300 МБ/с, Формат: M.2"},
    "блоки живлення": {"desc": "Надійний блок живлення із золотим сертифікатом.",
                       "specs": "Потужність: 850 Вт, Сертифікат: 80 Plus Gold, Модульний"},
    "корпуси": {"desc": "Стильний ігровий корпус із чудовим обдувом.",
                "specs": "Тип: Mid-Tower, Матеріал: Скло/Сталь, Вентилятори: 4 ARGB"},
    "охолодження": {"desc": "Потужна система водяного охолодження процесора.",
                    "specs": "Тип: СВО (водянка), Радіатор: 360мм, Кулери: 3x120мм"},
    "роутери": {"desc": "Двохдіапазонний швидкісний Wi-Fi роутер.",
                "specs": "Стандарт: Wi-Fi 6 (802.11ax), Швидкість: до 3000 Мбіт/с"},
    "павербанки": {"desc": "Потужна універсальна мобільна батарея швидкої зарядки.",
                   "specs": "Ємність: 20000 мАг, Потужність: 65W, Виходи: 2xUSB, 1xType-C"},
    "кабелі": {"desc": "Міцний кабель для швидкої зарядки та передачі даних.",
               "specs": "Інтерфейс: Type-C на Type-C, Довжина: 2м, Потужність: 100W"},
    "мікрофони": {"desc": "Студійний USB-мікрофон для стрімів та подкастів.",
                  "specs": "Спрямованість: Кардіоїда, Частоти: 20-20000 Гц, RGB підсвітка"}
}


# Вхід для клієнта (ПІБ + Email)
def customer_login(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if first_name and last_name and email:
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={'first_name': first_name, 'last_name': last_name}
            )
            request.session['customer_id'] = customer.customer_id
            request.session['customer_name'] = f"{customer.first_name} {customer.last_name}"
            request.session['is_admin'] = False
            messages.success(request, f"👋 Вітаємо, {customer.first_name}!")
            return redirect('menu')
    return render(request, 'login.html')


# Вхід для Адміна
def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['is_admin'] = True
            request.session['customer_id'] = None
            messages.success(request, "👑 Вхід в панель керування виконано!")
            return redirect('menu')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})


def user_logout(request):
    auth_logout(request)
    request.session.flush()
    messages.success(request, "🔒 Ви вийшли із системи.")
    return redirect('menu')


def index(request):
    cat_filter = request.GET.get('category', '').strip().lower()
    if cat_filter:
        products = Product.objects.filter(category=cat_filter)
    else:
        products = Product.objects.all()

    # Статистика продажів
    orders_all = Order.objects.all().select_related('product')
    total_sales = sum(item.product.price * item.quantity for item in orders_all)
    order_counts = Order.objects.count()
    avg_check = total_sales / order_counts if order_counts > 0 else 0
    popular_cat = Order.objects.values('product__category').annotate(count=Count('id')).order_by('-count').first()

    categories_list = Product.objects.values('category').annotate(count=Count('product_id'))

    return render(request, 'menu.html', {
        'products': products,
        'total_sales': round(total_sales, 2),
        'avg_check': round(avg_check, 2),
        'popular_cat': popular_cat,
        'categories': categories_list,
        'selected_category': cat_filter,
        'is_admin': request.session.get('is_admin', False),
        'customer_name': request.session.get('customer_name', None)
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'is_admin': request.session.get('is_admin', False)
    })


# Додавання відгуку (Бачать усі)
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        text = request.POST.get('text', '').strip()

        # Визначаємо автора відгуку
        if request.session.get('is_admin'):
            author = "Адміністратор"
        elif request.session.get('customer_name'):
            author = request.session.get('customer_name')
        else:
            author = "Гість"

        if text:
            Review.objects.create(product=product, author_name=author, text=text)
            messages.success(request, "💬 Відгук додано!")
    return redirect('product_detail', pk=product_id)


# --- ЛОГІКА КОШИКА (CART) ДЛЯ КОЖНОГО ОКРЕМОГО КЛІЄНТА ---
def get_cart_session_key(request):
    if request.session.get('is_admin'):
        return 'cart_admin'
    elif request.session.get('customer_id'):
        return f"cart_{request.session.get('customer_id')}"
    return 'cart_guest'


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_key = get_cart_session_key(request)
    cart = request.session.get(cart_key, {})

    p_id = str(product_id)
    if p_id in cart:
        if cart[p_id] < product.stock:
            cart[p_id] += 1
    else:
        cart[p_id] = 1

    request.session[cart_key] = cart
    messages.success(request, f"🛒 {product.name} додано в кошик!")
    return redirect('menu')


def cart_remove(request, product_id):
    cart_key = get_cart_session_key(request)
    cart = request.session.get(cart_key, {})
    p_id = str(product_id)
    if p_id in cart:
        del cart[p_id]
    request.session[cart_key] = cart
    return redirect('cart_detail')


def cart_detail(request):
    cart_key = get_cart_session_key(request)
    cart = request.session.get(cart_key, {})
    cart_items = []
    total_price = 0

    for p_id, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(p_id))
            item_total = product.price * qty
            total_price += item_total
            cart_items.append({'product': product, 'quantity': qty, 'item_total': item_total})
        except Product.DoesNotExist:
            continue

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def cart_checkout(request):
    cart_key = get_cart_session_key(request)
    cart = request.session.get(cart_key, {})

    if not request.session.get('customer_id') and not request.session.get('is_admin'):
        messages.error(request, "❌ Для оформлення замовлення потрібно увійти!")
        return redirect('login')

    if not cart:
        messages.error(request, "❌ Ваш кошик порожній!")
        return redirect('menu')

    # Якщо оформлює адмін, створимо віртуального клієнта "Адмін-Покупець"
    if request.session.get('is_admin'):
        customer, _ = Customer.objects.get_or_create(email='admin@shop.com',
                                                     defaults={'first_name': 'Головний', 'last_name': 'Адмін'})
    else:
        customer = get_object_or_404(Customer, pk=request.session.get('customer_id'))

    for p_id, qty in cart.items():
        product = get_object_or_404(Product, pk=int(p_id))
        if product.stock >= qty:
            Order.objects.create(customer=customer, product=product, quantity=qty)
            product.stock -= qty
            product.save()

    request.session[cart_key] = {}  # Очищаємо кошик після покупки
    messages.success(request, "🚀 Замовлення успішно оформлено з вашого кошика!")
    return redirect('menu')


# --- АДМІНСЬКІ ФУНКЦІЇ (ОБМЕЖЕННЯ ДОСТУПУ) ---
def add_product(request):
    if not request.session.get('is_admin'):
        return render(request, '403.html')  # Обмеження для простих користувачів
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category', '').strip().lower()
        price = float(request.POST.get('price', 0))
        stock = int(request.POST.get('stock', 0))
        description = request.POST.get('description')
        specs = request.POST.get('specs')

        Product.objects.create(name=name, category=category, price=price, stock=stock, description=description,
                               specs=specs)
        messages.success(request, "✅ Товар успішно додано!")
        return redirect('menu')
    return render(request, 'add_product.html', {'prompts': CATEGORY_PROMPTS})


def edit_product(request, pk):
    if not request.session.get('is_admin'):
        return render(request, '403.html')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name') or product.name
        product.price = float(request.POST.get('price') or product.price)
        product.stock = int(request.POST.get('stock') or product.stock)
        product.description = request.POST.get('description') or product.description
        product.specs = request.POST.get('specs') or product.specs
        product.save()
        messages.success(request, "✅ Товар оновлено!")
        return redirect('menu')
    return render(request, 'edit_product.html', {'product': product})


def add_customer(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        try:
            Customer.objects.create(first_name=first_name, last_name=last_name, email=email)
            messages.success(request, "✅ Клієнта успішно зареєстровано!")
            return redirect('login')
        except:
            messages.error(request, "❌ Такий Email вже існує!")
    return render(request, 'add_customer.html')


def show_customers(request):
    if not request.session.get('is_admin'):
        return render(request, '403.html')
    customers_list = Customer.objects.all()
    customers_data = []
    for c in customers_list:
        count = Order.objects.filter(customer=c).count()
        customers_data.append({'customer': c, 'order_count': count})
    return render(request, 'customers.html', {'customers_data': customers_data})


def show_orders(request):
    if not request.session.get('is_admin'):
        return render(request, '403.html')
    orders = Order.objects.all().select_related('customer', 'product')
    for order in orders:
        order.total_price = order.product.price * order.quantity
    return render(request, 'orders.html', {'orders': orders})


def update_prices(request):
    if not request.session.get('is_admin'): return render(request, '403.html')
    if request.method == 'POST':
        percentage = float(request.POST.get('percentage', 0))
        Product.objects.update(price=F('price') * (1 + percentage / 100.0))
        messages.success(request, f"📈 Ціни підвищено на {percentage}%!")
    return redirect('menu')


def decrease_prices(request):
    if not request.session.get('is_admin'): return render(request, '403.html')
    if request.method == 'POST':
        percentage = float(request.POST.get('percentage', 0))
        Product.objects.update(price=F('price') * (1 - percentage / 100.0))
        messages.success(request, f"📉 Ціни знижено на {percentage}%!")
    return redirect('menu')


def delete_item(request, item_type, pk):
    if not request.session.get('is_admin'): return render(request, '403.html')
    if item_type == 'product':
        get_object_or_404(Product, pk=pk).delete()
    elif item_type == 'customer':
        get_object_or_404(Customer, pk=pk).delete()
    elif item_type == 'order':
        get_object_or_404(Order, pk=pk).delete()
    messages.success(request, "🗑️ Запис видалено!")
    return redirect('menu')


def clear_table(request, table_name):
    if not request.session.get('is_admin'): return render(request, '403.html')
    if table_name == 'products':
        Product.objects.all().delete()
    elif table_name == 'customers':
        Customer.objects.all().delete()
    elif table_name == 'orders':
        Order.objects.all().delete()
    messages.success(request, "🗑️ Дані очищено!")
    return redirect('menu')