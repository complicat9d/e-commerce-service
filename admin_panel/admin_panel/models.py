from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)
    lang = models.CharField(max_length=2, default="en")


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)


# TODO: resolve problem with file  upload/depiction in admin panel
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to="photo/", null=True, blank=True)
    description = models.TextField()
    cost = models.FloatField()
    amount = models.IntegerField(default=0)


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    amount = models.IntegerField()
    cost = models.FloatField()
    address = models.CharField(max_length=255, null=True)
    is_being_delivered = models.BooleanField(default=False)


class FAQ(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
