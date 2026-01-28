from django import forms
from phonenumber_field.formfields import SplitPhoneNumberField, PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.conf import settings

from .models import EventInquiry, Product

bulk_order_input_class = "input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"

def get_flag_emoji(country_code):
    if not country_code or len(country_code) !=2:
        return ""
    return "".join(chr(ord(c) + 127397) for c in country_code.upper())

class FlagSplitPhoneNumberPrefixWidget(PhoneNumberPrefixWidget):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        choices = self.widgets[0].choices
        new_choices = []

        for code, label in choices:
            if code:
                flags = get_flag_emoji(str(code))
                new_label = label.split(" ").pop()
                new_choices.append((code, f"{flags} {new_label}"))
                
            else:
                new_choices.append((code, label))
        
        self.widgets[0].choices = new_choices


class FormSplitPhoneNumberField(SplitPhoneNumberField):
    widget = FlagSplitPhoneNumberPrefixWidget

    def prefix_field(self):
        return super().prefix_field()
    
    def number_field(self):
        number_field = super().number_field()
        number_field.widget.attrs["class"] = bulk_order_input_class
        number_field.widget.attrs["placeholder"] = "080..."
        return number_field


class BulkOrderForm(forms.ModelForm):
    package_choice = forms.ModelMultipleChoiceField(
        # empty_label="Select Package",
        queryset=Product.objects.all(),
        widget= forms.SelectMultiple(attrs={
            "class":"select select-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary font-bold",
        })
    )

    phone = FormSplitPhoneNumberField()
    class Meta:
        model = EventInquiry
        exclude = ["created_at", "status"]
        widgets = {
            "name":forms.TextInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"Enter name",
            }),
            # "phone":IntlTelInputWidget(attrs={
            #     "class":bulk_order_input_class,
            #     "type":"tel", 
            #     "placeholder":"080..."
            # },
            # default_code=settings.PHONENUMBER_DEFAULT_REGION.lower()),
            "event_type":forms.TextInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"Wedding, Party, etc."
            }),
            "event_date":forms.DateInput(attrs={
                "class":bulk_order_input_class,
                "type":"date"
            }),
            "guest_count":forms.NumberInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"e.g. 100"
            }),
            "location":forms.TextInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"e.g. Victoria Island, Lagos"
            }),
            "notes":forms.Textarea(attrs={
                "class":"textarea textarea-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"
            }),

        }
