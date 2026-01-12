from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='chops/')
    is_available = models.BooleanField(default=True) # The toggle we built
    is_featured = models.BooleanField(default=False) # For the home page hero

    def __str__(self):
        return self.name
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('preparing', 'In the Fryer'),
        ('ready', 'Ready to Pack'),
        ('shipped', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    delivery_zone = models.ForeignKey("vendor.DeliveryZone", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_ref = models.CharField(max_length=100, blank=True) # For Paystack
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = "-created_at"

    def __str__(self):
        return f"Order #{self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True) # e.g. "No pepper"

class EventInquiry(models.Model):
    STATUS = [('new', 'New'), ('contacted', 'Contacted'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    event_type = models.CharField(max_length=100) # Wedding, Party, etc.
    event_date = models.DateField()
    guest_count = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    package_choice = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)