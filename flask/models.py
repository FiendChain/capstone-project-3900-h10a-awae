from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length = 200)
    price = models.FloatField()
    brand = models.CharField(max_length = 200)
    category = models.CharField(max_length = 200)
    description = models.CharField(max_length = 1000)
    delivery = models.IntegerField()
    warranty = models.IntegerField()
    image_link = models.CharField(max_length = 200)

class User(models.Model):
    id = models.IntegerField(primary_key = True)
    username = models.CharField(max_length = 200)
    password = models.CharField(max_length = 200)
    email = models.CharField(max_length = 200)
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)
    dob = models.DateField()
    is_admin = models.BooleanField()

class Cart(models.Model):
    id = models.IntegerField(primary_key = True)
    user_id = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
    )

class CartItem(models.Model):
    id = models.IntegerField(primary_key = True)
    cart_id = models.ForeignKey(
        Cart,
        on_delete = models.CASCADE
    )
    product_id = models.ForeignKey(
        Product,
        on_delete = models.CASCADE
    )