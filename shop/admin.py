from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderPack, OrderItem, EventInquiry

# --- INLINES ---

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_cost',)

class OrderPackInline(admin.StackedInline):
    model = OrderPack
    extra = 0
    show_change_link = True # Allows you to click into the pack specifically

# --- MODEL ADMINS ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Display the emoji and name clearly in the list view
    list_display = ('display_icon', 'name', 'slug')
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    # This makes the emoji look big and central in the admin table
    def display_icon(self, obj):
        return format_html(
            '<span style="font-size: 24px; background: #f3f4f6; padding: 5px 10px; border-radius: 50%;">{}</span>', 
            obj.icon_emoji
        )
    display_icon.short_description = 'Icon'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('display_image', 'name', 'category_with_icon', 'price', 'is_available', 'is_featured')
    list_editable = ('price', 'is_available', 'is_featured') # Edit directly from the list view
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name',)

    def category_with_icon(self, obj):
        return f"{obj.category.icon_emoji} {obj.category.name}"
    category_with_icon.short_description = 'Category'

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 8px;" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Preview'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status_colored', 'name', 'total_amount', 'paid', 'created_at')
    list_filter = ('status', 'paid', 'created_at', 'delivery_zone')
    search_fields = ('name', 'phone', 'payment_ref')
    readonly_fields = ('payment_ref', 'created_at')
    inlines = [OrderPackInline]
    
    # Custom colored status labels for quick scanning
    def status_colored(self, obj):
        colors = {
            'pending': '#eab308',   # Yellow
            'preparing': '#3b82f6', # Blue
            'ready': '#a855f7',     # Purple
            'shipped': '#f97316',   # Orange
            'delivered': '#22c55e', # Green
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 8px; border-radius: 12px; font-weight: bold; text-transform: uppercase; font-size: 10px;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'

@admin.register(OrderPack)
class OrderPackAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'item_count')
    inlines = [OrderItemInline]

    def item_count(self, obj):
        return obj.items.count()

@admin.register(EventInquiry)
class EventInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'event_date', 'guest_count', 'status')
    list_filter = ('status', 'event_date', 'created_at')
    search_fields = ('name', 'phone', 'location')
    date_hierarchy = 'event_date' # Adds a date navigation bar at the top