from django.db import models

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    specs = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_with='products/', blank=True, null=True) # Фото додаси завтра

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField()

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order {self.order_id} by {self.customer}"


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', db_column='product_id')
    author_name = models.CharField(max_length=255)  # Ім'я того, хто залишив відгук
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.author_name} on {self.product.name}"