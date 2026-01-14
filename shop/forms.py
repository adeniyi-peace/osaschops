from django import forms

from .models import EventInquiry, Product

bulk_order_input_class = "input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"


class BulkOrderForm(forms.ModelForm):
    package_choice = forms.ModelMultipleChoiceField(
        # empty_label="Select Package",
        queryset=Product.objects.all(),
        widget= forms.SelectMultiple(attrs={
            "class":"select select-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary font-bold",
        })
    )
    class Meta:
        model = EventInquiry
        exclude = ["created_at", "status"]
        widgets = {
            "name":forms.TextInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"Enter name",
            }),
            "phone":forms.TextInput({
                "class":bulk_order_input_class,
                "type":"tel", 
                "placeholder":"080..."
            }),
            "event_type":forms.TextInput(attrs={
                "class":bulk_order_input_class,
            }),
            "event_date":forms.DateInput(attrs={
                "class":bulk_order_input_class,
            }),
            "guest_count":forms.NumberInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"e.g. 100"
            }),
            "location":forms.TextInput(attrs={
                "class":bulk_order_input_class,
                "placeholder":"e.g. Victoria Island, Lagos"
            }),
            "note":forms.Textarea(attrs={
                "class":"textarea textarea-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"
            }),

        }
