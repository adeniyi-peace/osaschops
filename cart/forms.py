from django import forms

from shop.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ["status","created_at","total_amount"]