from django.db import models
from django.utils.text import slugify

class StoreSetting(models.Model):
    name = models.CharField(max_length=100, default="Osaschops")
    logo = models.ImageField(upload_to='logos/', blank=True)
    whatsapp_number = models.CharField(max_length=20, help_text="Format: 2348053384458")

    hero_badge = models.CharField(max_length=50, default="✨ NEW MONTH, NEW LEVELS!")
    hero_title = models.CharField(max_length=200, default="Chops Wey Get Levels")
    hero_subtitle = models.TextField(default="Celebrating a new month with the crunchiest Samosas...")
    hero_image = models.ImageField(upload_to='hero/', blank=True, null=True)

    def __str__(self):
        return self.name

class BusinessDay(models.Model):
    DAYS = [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]
    day = models.IntegerField(choices=DAYS, unique=True)
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(default="09:00")
    closing_time = models.TimeField(default="21:00")

    class Meta:
        ordering = ['day']

class DeliveryZone(models.Model):
    name = models.CharField(max_length=100) # e.g., Lekki Phase 1
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (₦{self.fee})"