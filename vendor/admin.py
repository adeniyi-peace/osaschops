from django.contrib import admin
from django.utils.html import format_html
from .models import StoreSetting, BusinessDay, DeliveryZone

@admin.register(StoreSetting)
class StoreSettingAdmin(admin.ModelAdmin):
    # Grouping fields to make the settings page cleaner
    fieldsets = (
        ('Branding & Contact', {
            'fields': ('name', 'logo', 'whatsapp_number')
        }),
        ('Hero Section (Homepage)', {
            'fields': ('hero_badge', 'hero_title', 'hero_subtitle', 'hero_image'),
            'description': 'These settings control the main banner at the top of your website.'
        }),
    )

    def has_add_permission(self, request):
        # Prevents creating more than one settings object
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(BusinessDay)
class BusinessDayAdmin(admin.ModelAdmin):
    list_display = ('get_day_display', 'is_open', 'opening_time', 'closing_time')
    list_editable = ('is_open', 'opening_time', 'closing_time')
    list_display_links = ('get_day_display',)

@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_fee')
    # list_editable = ('name',) # Allow quick renaming
    search_fields = ('name',)

    def formatted_fee(self, obj):
        return format_html('<b>₦{:,.2f}</b>', obj.fee)
    formatted_fee.short_description = 'Delivery Fee'