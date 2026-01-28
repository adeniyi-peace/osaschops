from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField

from shop.models import Order
from shop.forms import FlagSplitPhoneNumberPrefixWidget


class FormSplitPhoneNumberField(SplitPhoneNumberField):
    widget = FlagSplitPhoneNumberPrefixWidget

    def prefix_field(self):
        return super().prefix_field()
    
    def number_field(self):
        number_field = super().number_field()
        number_field.widget.attrs["class"] = "input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full"
        number_field.widget.attrs["placeholder"] = "080..."
        return number_field

class OrderForm(forms.ModelForm):
    phone = FormSplitPhoneNumberField()

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
            "address" : forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":"House number and street name"
            }),
            "delivery_zone" : forms.Select(attrs={
                "class":"select select-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "onchange":"handleDeliveryZoneChange(this)"
            },),
            "payment_ref" : forms.RadioSelect(attrs={
                "class":"radio radio-primary"
            },
            choices=(("Paystack (Card/Transfer)", "Paystack (Card/Transfer)"),("Pay on Delivery", "Pay on Delivery"))),
            "delivery_note":forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary w-full",
                "placeholder":"Gate code or landmarks"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["delivery_zone"].empty_label = "Select Area"