from django.db import models

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    description = models.TextField(default="Немає опису")
    specs = models.TextField(default="Не вказано")

    class Meta:
        app_label = 'myproject'

    def __str__(self):
        return self.name

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        app_label = 'myproject'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'myproject'

    def __str__(self):
        return f"Замовлення {self.id} - {self.customer.last_name}"