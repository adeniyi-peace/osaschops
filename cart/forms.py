from django import forms

from shop.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ["status","created_at","total_amount"]
        widgets = {
            "name" : forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":"e.g. Osas Ighodaro"
            }),
            "email" : forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":""
            }),
            "phone" : forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":"080XXXXXXXX"
            }),
            "address" : forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":"House number and street name"
            }),
            "delivery_zone" : forms.Select(attrs={
                "class":"select select-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":"House number and street name"
            }),
            "status" : "",
            "payment_ref" : "",
        }