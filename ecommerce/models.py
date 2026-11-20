"""Models for the eCommerce app."""
from django.db import models
from django.contrib.auth.models import User


class Store(models.Model):
    # the vendor who owns the store
    """A store that belongs to a vendor."""

    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return the store name."""
        return self.name


class Product(models.Model):
    """A product that is sold in a store."""

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        """Return the product name."""
        return self.name


class Order(models.Model):
    # this is the invoice that gets made when a buyer checks out
    """An order (invoice) made when a buyer checks out."""

    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        """Return the order number and the buyer."""
        return f"Order {self.id} by {self.buyer.username}"


class OrderItem(models.Model):
    """One product and its quantity inside an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # If deleted, keep the product name and price on the order.
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Return the quantity and the product name."""
        return f"{self.quantity} x {self.product_name}"


class Review(models.Model):
    """A review a buyer leaves on a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1 to 5
    comment = models.TextField()
    # True if the buyer actually bought the product
    verified = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the buyer and the product name."""
        return f"{self.buyer.username} - {self.product.name}"


class ResetToken(models.Model):
    # used for the forgot password link (same as the lesson)
    """A token used for the forgot password link."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)
