from django import forms

from shop.models import Product
from . models import BusinessDay, StoreSetting, DeliveryZone

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["is_featured", "is_available"]
        widgets = {
            "name":forms.TextInput(attrs={
                "class": "input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"
            }),
            "category":forms.Select(attrs={
                "class": "select select-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"
            }),
            "price":forms.NumberInput(attrs={
                "class": "input input-bordered rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"
            }),
            "image":forms.FileInput(attrs={
                "class":"file-input file-input-bordered file-input-primary w-full rounded-xl bg-base-200 border-none"
            }),
            "description":forms.Textarea(attrs={
                "class":"textarea textarea-bordered  rounded-xl bg-base-200 border-none focus:ring-2 focus:ring-primary"
            }),
        }


class BusinessDayForm(forms.ModelForm):
    
    class Meta:
        model = BusinessDay
        fields = ["day", "is_open", "opening_time", "closing_time"]
        widgets = {
            "day":forms.HiddenInput(),
            "is_open":forms.CheckboxInput(attrs={
                "class":"toggle toggle-primary toggle-sm day-toggle",
                "onclick":"toggleTimeInputs(this)",
            }),
            "opening_time":forms.TimeInput(attrs={
                "class":"input input-sm w-full rounded-lg border-cream font-bold text-xs focus:ring-1 focus:ring-primary time-input",
                "type":"time",
                "value":"09:00"
            }),
            "closing_time":forms.TimeInput(attrs={
                "class":"input input-sm w-full rounded-lg border-cream font-bold text-xs focus:ring-1 focus:ring-primary time-input",
                "type":"time",
                "value":"09:00"
            })
        }

    def has_changed(self):
        # A form with a day field is always considered to have changed.
        # This forces Django to process forms for days that were not checked.
        if 'day' in self.initial:
            return True
        return super().has_changed()


BaseOpenFormset = forms.modelformset_factory(
    BusinessDay,
    form = BusinessDayForm,
    fields = ["day", "is_open", "opening_time", "closing_time"],
    extra = 0,
    can_delete = False,
)

class BusinessDayFormSet(BaseOpenFormset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # check if there are already 7 forms
        if self.queryset.count() < 7:
            # get existing days
            existing_days = self.queryset.values_list("day", flat=True)
            
            # create a form instance for each missing day
            for day in range(7):
                if day not in existing_days:
                    # Add a new form instance
                    form = self._construct_form(len(self.forms))
                    form.initial['day'] = day
                    self.forms.append(form)

        # label each form with day of the week
        for form in self.forms:
            # `form.initial.get("day")` handles existing form
            # `form.data.get(...)` handles new form submissions
            day_index = form.data.get(form.prefix + "-day") or form.initial.get("day")

            if day_index is not None:
                form.fields["day"].label = BusinessDay.DAYS[int(day_index)][1]
                # form.fields["day"].label = BusinessDay.DAYS(day_index).label


class StoreSettingForm(forms.ModelForm):
    class Meta:
        model = StoreSetting
        exclude = ["name"]
        widgets = {
            "hero_badge":forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none font-bold"
            }),
            "hero_title":forms.TextInput(attrs={
                "class":"input input-bordered rounded-xl bg-base-200 border-none font-bold"
            }),
            "hero_subtitle":forms.TextInput(attrs={
                "class":"textarea textarea-bordered rounded-xl bg-base-200 border-none font-medium h-24"
            }),
            "hero_image":forms.FileInput(attrs={
                "class":"file-input file-input-bordered file-input-primary w-full rounded-xl bg-base-200 border-none"
            }),
            "whatsapp_number":forms.TextInput({
                "class":"input input-bordered grow rounded-xl bg-base-200 border-none font-bold"
            }),
            "logo":forms.FileInput(attrs={
                "class":"file-input file-input-bordered file-input-primary w-full rounded-xl bg-base-200 border-none"
            }),
        }

class DeliveryZoneForm(forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = "__all__"
        widgets = {
            "name":forms.TextInput(attrs={
                "class":"input input-sm w-full rounded-lg border-cream font-black text-primary"
            }),
            "fee":forms.NumberInput(attrs={
                "class":"input input-sm w-full rounded-lg border-cream font-black text-primary"
            })
        }

DeliveryZoneFormset = forms.modelformset_factory(
    model=DeliveryZone,
    form = DeliveryZoneForm,
    can_delete=True,
    extra=1,
)
