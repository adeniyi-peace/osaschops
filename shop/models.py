from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from .utils import compress_image

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon_emoji = models.CharField(
        max_length=10, 
        default="🥟", 
        help_text="Enter a single emoji (e.g., 🍗, 🥤, 🍱)"
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image

    def save(self, *args, **kwargs):
        if self.image != self._original_image:
            compress_image(self.image, 1100)
        return super().save(*args, **kwargs)
        

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
    phone = PhoneNumberField()
    address = models.TextField()
    delivery_zone = models.ForeignKey("vendor.DeliveryZone", on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_ref = models.CharField(max_length=100, blank=True) # For Paystack
    delivery_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.name}"


class OrderPack(models.Model):
    order = models.ForeignKey(Order, related_name='packs', on_delete=models.CASCADE)
    name = models.CharField(max_length=100) # e.g., "Pack 1" or "Wedding Guest Pack"
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    # Now linked to OrderPack, not directly to Order
    pack = models.ForeignKey(OrderPack, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity

class EventInquiry(models.Model):
    STATUS = [('new', 'New'), ('contacted', 'Contacted'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]
    
    name = models.CharField(max_length=200)
    phone = PhoneNumberField()
    event_type = models.CharField(max_length=100) # Wedding, Party, etc.
    event_date = models.DateField()
    guest_count = models.PositiveIntegerField()
    location = models.CharField(max_length=255)
    package_choice = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)