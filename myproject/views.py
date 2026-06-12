from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Avg, Count, F
from .models import Product, Customer, Order

CATEGORY_PROMPTS = {
    "смартфони": {
        "desc": "Флагманський смартфон із передовими технологіями, чудовою камерою та високою продуктивністю.",
        "specs": "Екран: 6.7 OLED, Процесор: A17 Pro, Пам'ять: 256 ГБ, Камера: 48+12+12 Мп, Акумулятор: 4441 мАг"
    },
    "планшети": {
        "desc": "Потужний і компактний планшет для навчання, роботи, творчості та перегляду медіаконтенту.",
        "specs": "Екран: 11 IPS, Процесор: Apple M2, Пам'ять: 128 ГБ, Оперативна пам'ять: 8 ГБ, ОС: iPadOS"
    },
    "ноутбуки": {
        "desc": "Високопродуктивний ноутбук для програмування, складних робочих завдань та сучасних ігор.",
        "specs": "Екран: 16 IPS 165Гц, Процесор: Core i7-13700H, Відеокарта: RTX 4060, ОЗУ: 16 ГБ, SSD: 1 ТБ"
    },
    "комп'ютери": {
        "desc": "Потужний системний блок для геймінгу на ультра-налаштуваннях та роботи з важкою графікою.",
        "specs": "Процесор: Ryzen 7 7800X3D, Відеокарта: RTX 4070 Ti, ОЗУ: 32 ГБ DDR5, SSD: 2 ТБ NVMe, БП: 850W"
    },
    "монітори": {
        "desc": "Ігровий монітор із високою частотою оновлення для максимальної плавності динамічних змін.",
        "specs": "Діагональ: 27, Матриця: IPS, Роздільна здатність: 2560x1440 (2K), Частота: 144 Гц, Час відгуку: 1 мс"
    },
    "телевізори": {
        "desc": "Сучасний телевізор із підтримкою Smart TV та реалістичною картинкою високої чіткості.",
        "specs": "Діагональ: 55, Екран: 4K Ultra HD Neo QLED, Smart TV: ОС Tizen, Звук: 60 Вт, Частота: 120 Гц"
    },
    "навушники": {
        "desc": "Повнорозмірні бездротові навушники з активним шумозаглушенням та преміальним звучанням.",
        "specs": "Тип: Повнорозмірні, Підключення: Bluetooth 5.2 / Дротове, Шумозаглушення: ANC, Час роботи: до 30 год"
    },
    "колонки": {
        "desc": "Портативна бездротова акустична система із глибоким басом та захистом від води.",
        "specs": "Потужність: 40 Вт, Захист: IP67, Акумулятор: 7500 мАг, Час роботи: до 20 год, Інтерфейси: Bluetooth 5.1"
    },
    "годинники": {
        "desc": "Смарт-годинник преміум-класу для відстеження фізичної активності, тренувань та показників здоров'я.",
        "specs": "Екран: 1.92 OLED, Матеріал: Титан, Сапфірове скло, Датчики: Пульсометр, ЕКГ, SpO2, Вологозахист: 100м"
    },
    "приставки": {
        "desc": "Ігрова консоль нового покоління для неймовірного геймінгу у високій роздільній здатності.",
        "specs": "Процесор: AMD Zen 2, Графіка: RDNA 2, Пам'ять: 825 ГБ SSD, Підтримка: 4K 120Hz, Комплектація: 1 геймпад"
    },
    "ігри": {
        "desc": "Масштабна пригодницька гра з відкритим світом, захоплюючим сюжетом та сучасною графікою.",
        "specs": "Платформа: PlayStation 5, Жанр: RPG / Action, Носій: Blu-ray Диск, Локалізація: Повна українська версія"
    },
    "мишки": {
        "desc": "Бездротова кіберспортивна ігрова миша з надлегким корпусом та високоточним оптичним сенсором.",
        "specs": "Сенсор: Оптичний 30000 DPI, Кількість кнопок: 5, Вага: 63 г, Підключення: Бездротове / USB, Час роботи: 90 год"
    },
    "клавіатури": {
        "desc": "Механічна ігрова клавіатура з надійними перемикачами та яскравим підсвічуванням клавіш.",
        "specs": "Тип: Механічна, Перемикачі: Cherry MX Red, Формат: TKL (80%), Підсвічування: RGB, Матеріал корпусу: Алюміній"
    },
    "відеокарти": {
        "desc": "Топова графічна карта для забезпечення максимального FPS у сучасних іграх при 4K та трасуванні променів.",
        "specs": "Пам'ять: 16 ГБ GDDR6X, Шина пам'яті: 256 біт, Частота: 2610 МГц, Інтерфейс: PCI Express 4.0, Кулери: 3"
    },
    "процесори": {
        "desc": "Високопродуктивний багатоядерний процесор для потужних ігрових систем та складних обчислень.",
        "specs": "Сокет: AM5, Кількість ядер: 8, Кількість потоків: 16, Базова частота: 4.2 ГГц, Максимальна: 5.0 ГГц"
    },
    "пам'ять": {
        "desc": "Швидкісний комплект оперативної пам'яті нового покоління для підвищення стабільності та швидкості системи.",
        "specs": "Тип: DDR5, Об'єм: 32 ГБ (2x16 ГБ), Частота: 6000 МГц, Таймінги: CL30, Підсвічування: RGB"
    },
    "накопичувачі": {
        "desc": "Швидкісний твердотільний накопичувач для миттєвого завантаження системи, програм та ігор.",
        "specs": "Тип: SSD M.2 NVMe, Об'єм: 1 ТБ, Швидкість читання: 7300 МБ/с, Швидкість запису: 6000 МБ/с, Інтерфейс: PCIe 4.0"
    },
    "материнські плати": {
        "desc": "Надійна материнська плата з потужною системою живлення та широкими можливостями розширення.",
        "specs": "Чіпсет: Intel Z790, Сокет: LGA1700, Форм-фактор: ATX, Слоти ОЗУ: 4xДДR5, Бездротові технології: Wi-Fi 6E, Bluetooth"
    },
    "повербанки": {
        "desc": "Універсальний зовнішній акумулятор великої ємності з можливістю швидкої зарядки кількох пристроїв.",
        "specs": "Ємність: 20000 мАг, Потужність: 65 Вт, Порти: 2xUSB, 1xType-C, Технології: Power Delivery, Quick Charge 3.0"
    },
    "роутери": {
        "desc": "Двохдіапазонний гігабітний маршрутизатор для створення стабільного бездротового покриття у великому домі.",
        "specs": "Стандарт: Wi-Fi 6 (802.11ax), Швидкість: до 2976 Мбіт/с, Порти: 4xLAN 1Гбіт/с, 1xWAN 1Гбіт/с, Антени: 4"
    },
    "принтери": {
        "desc": "БФП з кольоровим струменевим друком та вбудованою фабрикою чорнила для економного виготовлення документів.",
        "specs": "Тип: Струменевий кольоровий, Функції: Друк, сканування, копіювання, Інтерфейси: Wi-Fi, USB, СБПЧ: вбудована"
    },
    "камери": {
        "desc": "Бездзеркальна цифрова фотокамера зі змінною оптикою для професійної зйомки фото та відео.",
        "specs": "Матриця: 24.2 Мп Full-Frame, Відео: 4K 60p, Екран: Поворотний 3.0 сенсорний, Стабілізація: 5-осьова вбудована"
    },
    "дрони": {
        "desc": "Квадрокоптер із високоякісною камерою та інтелектуальними режимами польоту для чудових аерознімків.",
        "specs": "Камера: 4K CMOS, Час польоту: до 34 хв, Дальність: до 12 км, Вага: 249 г, Датчики: виявлення перешкод"
    },
    "кабелі": {
        "desc": "Надійний екранований кабель для швидкої передачи даних та високопотужної зарядки пристроїв.",
        "specs": "Тип роз'ємів: Type-C - Type-C, Довжина: 1.2 м, Пропускна здатність: 100W, Матеріал: Нейлонове обплетення"
    },
    "побутова техніка": {
        "desc": "Розумний робот-пилосос для щоденного сухого та вологого прибирання підлогових покриттів.",
        "specs": "Потужність всмокування: 5000 Па, Навігація: LiDAR, Акумулятор: 5200 мАг, Керування: Додаток Mi Home"
    }
}

def index(request):
    cat_filter = request.GET.get('category', '').strip().lower()
    if cat_filter:
        products = Product.objects.filter(category=cat_filter)
    else:
        products = Product.objects.all()

    orders_all = Order.objects.all().select_related('product')
    total_sales = sum(item.product.price * item.quantity for item in orders_all)

    order_counts = Order.objects.count()
    avg_check = total_sales / order_counts if order_counts > 0 else 0

    popular_cat = Order.objects.values('product__category').annotate(count=Count('id')).order_by('-count').first()
    products_per_cat = Product.objects.values('category').annotate(count=Count('product_id'))

    return render(request, 'menu.html', {
        'products': products,
        'total_sales': round(total_sales, 2),
        'avg_check': round(avg_check, 2),
        'popular_cat': popular_cat,
        'products_per_cat': products_per_cat,
        'selected_category': cat_filter
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category', '').strip().lower()
        price = float(request.POST.get('price', 0))
        stock = int(request.POST.get('stock', 0))
        description = request.POST.get('description')
        specs = request.POST.get('specs')

        Product.objects.create(name=name, category=category, price=price, stock=stock, description=description, specs=specs)
        messages.success(request, "✅ Товар успішно додано!")
        return redirect('menu')

    return render(request, 'add_product.html', {'prompts': CATEGORY_PROMPTS})

def edit_product(request, pk):
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
            messages.success(request, "✅ Клієнта додано!")
            return redirect('menu')
        except:
            messages.error(request, "❌ Такий Email вже існує!")
            return redirect('add_customer')
    return render(request, 'add_customer.html')

def show_customers(request):
    customers_list = Customer.objects.all()
    customers_data = []
    for c in customers_list:
        count = Order.objects.filter(customer=c).count()
        customers_data.append({'customer': c, 'order_count': count})
    return render(request, 'customers.html', {'customers_data': customers_data})

def create_order(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        product_id = request.POST.get('product')
        quantity = int(request.POST.get('quantity', 0))

        product = get_object_or_404(Product, pk=product_id)
        customer = get_object_or_404(Customer, pk=customer_id)

        if product.stock <= 0:
            messages.error(request, f"❌ '{product.name}' закінчився!")
            return redirect('create_order')
        if quantity <= 0 or quantity > product.stock:
            messages.error(request, f"❌ Доступно лише {product.stock} шт.")
            return redirect('create_order')

        Order.objects.create(customer=customer, product=product, quantity=quantity)
        product.stock -= quantity
        product.save()

        messages.success(request, "✅ Замовлення оформлено!")
        return redirect('menu')

    return render(request, 'order_form.html', {'customers': Customer.objects.all(), 'products': Product.objects.all()})

def show_orders(request):
    orders = Order.objects.all().select_related('customer', 'product')
    return render(request, 'orders.html', {'orders': orders})

def update_prices(request):
    if request.method == 'POST':
        percentage = float(request.POST.get('percentage', 0))
        factor = 1 + (percentage / 100.0)
        Product.objects.update(price=F('price') * factor)
        messages.success(request, f"📈 Ціни підвищено на {percentage}%!")
    return redirect('menu')

def decrease_prices(request):
    if request.method == 'POST':
        percentage = float(request.POST.get('percentage', 0))
        factor = 1 - (percentage / 100.0)
        Product.objects.update(price=F('price') * factor)
        messages.success(request, f"📉 Ціни знижено на {percentage}%!")
    return redirect('menu')

def delete_item(request, item_type, pk):
    if item_type == 'product':
        get_object_or_404(Product, pk=pk).delete()
    elif item_type == 'customer':
        get_object_or_404(Customer, pk=pk).delete()
    elif item_type == 'order':
        get_object_or_404(Order, pk=pk).delete()
    messages.success(request, "🗑️ Запис видалено!")
    return redirect('menu')

def clear_table(request, table_name):
    if table_name == 'products':
        Product.objects.all().delete()
    elif table_name == 'customers':
        Customer.objects.all().delete()
    elif table_name == 'orders':
        Order.objects.all().delete()
    messages.success(request, "🗑️ Дані очищено!")
    return redirect('menu')