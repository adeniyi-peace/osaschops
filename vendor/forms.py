from django import forms

from shop.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["is_featured", "is_available"]