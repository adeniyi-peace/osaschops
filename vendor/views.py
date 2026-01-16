from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, F, ExpressionWrapper, DurationField, Avg, Q
from django.db.models.functions import Now
from django.http import JsonResponse
from django.template.loader import render_to_string
import json

from shop.models import Order, OrderItem, Product, EventInquiry, Category
from . models import BusinessDay, DeliveryZone, StoreSetting
from . forms import ProductForm, BusinessDayFormSet, DeliveryZoneFormset, StoreSettingForm

class DashboardView(View):
    def get(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Revenue calculations
        today_revenue = Order.objects.filter(created_at__date=today, paid=True).aggregate(total=Sum("total_amount"))["total"] or 0
        yesterday_revenue = Order.objects.filter(created_at__date=yesterday, paid=True).aggregate(total=Sum("total_amount"))["total"] or 0
        
        percentage = 0
        if yesterday_revenue > 0:
            percentage = round(((today_revenue - yesterday_revenue) / yesterday_revenue) * 100)

        current_revenue = f"↗︎ {percentage}% vs yesterday" if percentage >= 0 else f"↘︎ {abs(percentage)}% vs yesterday"

        # Refactored: Fetch orders with their packs and items
        recent_orders = Order.objects.filter(status="pending").prefetch_related(
            "packs__items__product"
        )

        # Refactored: Count products through the OrderItem -> OrderPack link
        top_chops = Product.objects.annotate(
            best_seller=Count("order_items") # order_items is related_name in OrderItem model
        ).order_by("-best_seller")[:3]

        context = {
            "current_revenue": current_revenue,
            "today_revenue": today_revenue,
            "recent_orders": recent_orders,
            "top_chops": top_chops,
            "percentage": percentage
        }
        return render(request, "vendor/dashboard_page.html", context)

        
    
class OrderView(View):
    def get(self, request):
        active_orders = Order.objects.exclude(status="delivered").prefetch_related(
            'packs__items__product'
        ).select_related('delivery_zone')

        context = {
            "active_orders":active_orders,
        }

        return render(request, "vendor/order_page.html", context)

class OrderReceiptView(View):
    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related('packs__items__product'), 
            id=order_id
        )
        return render(request, "vendor/order_receipt.html", {"order": order})


class UpdateOrderStatusView(View):
    def post(self, request, order_id):
        data = json.loads(request.body)
        new_status = data.get('status')
        order = get_object_or_404(Order, id=order_id)
        
        order.status = new_status
        order.save()

        # Trigger WhatsApp only when shipping
        if new_status == 'shipped':
            # send_whatsapp_update(order)
            ...

        return JsonResponse({'success': True})
    

class SalesReportView(TemplateView):
    template_name = 'vendor/report_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Date Range Handling (Default to last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # 2. Key Metrics
        orders_queryset = Order.objects.filter(status='delivered')
        total_revenue = orders_queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = orders_queryset.count()
        avg_order_value = orders_queryset.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        
        # 3. Event Metrics
        total_inquiries = EventInquiry.objects.count()
        confirmed_inquiries = EventInquiry.objects.filter(status='confirmed').count()
        conversion_rate = (confirmed_inquiries / total_inquiries * 100) if total_inquiries > 0 else 0

        # 4. Category Performance (For the Progress Bars)
        # We find how many items were sold per category
        category_data = Category.objects.annotate(
            sold_count=Count('products__orderitem')
        ).order_by('-sold_count')[:3]

        # 5. Loyal Customers (Table Logic)
        loyal_customers = Order.objects.values('customer_email', 'customer_name') \
            .annotate(order_count=Count('id'), total_spend=Sum('total_amount')) \
            .order_by('-total_spend')[:5]

        # 6. Revenue Trend Logic (Simplified for the Bar Chart)
        # This gets revenue for the last 6 days
        trend_data = []
        for i in range(5, -1, -1):
            day = end_date - timedelta(days=i)
            day_revenue = Order.objects.filter(
                created_at__date=day.date(), 
                status='delivered'
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            trend_data.append({
                'day': day.strftime('%a'),
                'amount': day_revenue
            })

        # Calculate max for chart scaling
        max_rev = max([d['amount'] for d in trend_data]) if trend_data else 1

        context.update({
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'total_inquiries': total_inquiries,
            'conversion_rate': conversion_rate,
            'category_data': category_data,
            'loyal_customers': loyal_customers,
            'trend_data': trend_data,
            'max_rev': max_rev,
        })
        return context

class MenuListView(View):

    def get(self, request):
        product = Product.objects.all()
        form = ProductForm()
        search_query = request.GET.get('search')
        
        if search_query:
            product = product.filter(
                Q(name__icontains=search_query) | 
                Q(category__name__icontains=search_query)
            )
        
        context = {
            "menu_item":product,
            "form":form,
        }
        
        return render(request, "vendor/menu_page.html", context)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            pk = data.get("itemId")
            is_available = data.get('available')
            
            # Update the product
            product = Product.objects.get(pk=pk)
            product.is_available = is_available
            product.save()
            
            return JsonResponse({'success': True})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class AddEditProductView(View):
    """View to return the partial HTML for Add or Edit"""
    def get(self, request, pk=None):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            form = ProductForm(instance=product)
        else:
            form = ProductForm()
            
        return render(request, 'vendor/includes/product_form.html', {'form': form})
    
    def post(self, request, pk=None):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            form = ProductForm(request.POST, request.FILES, instance=product)
        else:
            form = ProductForm(request.POST, request.FILES)

            if form.is_valid():
                form.save()

                return JsonResponse({'success': True, })

        context = {
            "form":form
        }

        html = render_to_string(
            'vendor/includes/product_form.html', context, request
        )

        return JsonResponse({'success': False, 'html': html}, status=400)
                        

class ProductDeleteView(View):
    """View to return the delete confirmation partial"""
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'vendor/includes/delete_confirm.html', {'item': product})
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect("vendor_menu")


class SettingsView(View):
    def get(self, request):
        business_day = BusinessDay.objects.all()
        delivery_zone = DeliveryZone.objects.all()
        # store_settings = get_object_or_404(StoreSetting, name="Osaschops")
        store_settings = DeliveryZone.objects.all()
        business_formset = BusinessDayFormSet(queryset=business_day)
        delivery_formset = DeliveryZoneFormset(queryset=delivery_zone, prefix="delivery_zone")
        # store_form = StoreSettingForm(instance=store_settings)
        store_form = StoreSettingForm()

        context = {
            "business_formset":business_formset,
            "delivery_formset":delivery_formset,
            "store_form":store_form,
            "store_settings":store_settings,
        }

        return render(request, "vendor/settings_page.html", context)

    def post(self, request):
        business_day = BusinessDay.objects.all()
        delivery_zone = DeliveryZone.objects.all()
        store_settings = get_object_or_404(StoreSetting, name="Osaschops")
        business_formset = BusinessDayFormSet(request.POST, request.FILES, queryset=business_day)
        delivery_formset = DeliveryZoneFormset(request.POST, request.FILES, queryset=delivery_zone, prefix="delivery_zone")
        store_form = StoreSettingForm(request.POST, request.FILES, instance=store_settings)

        if business_formset.is_valid() and delivery_formset.is_valid() and store_form.is_valid():
            business_formset.save()
            delivery_formset.save()
            store_form.save()

            return redirect("...")

        context = {
            "business_formset":business_formset,
            "delivery_formset":delivery_formset,
            "store_form":store_form,
            "store_settings":store_settings,
        }

        return render(request, "vendor/settings.html", context)
        

class EventInquiryView(View):
    def get(self, request):
        query= EventInquiry.objects.all()
        inquiries = query.filter(status__in=["new","contacted"])
        new_inquires = query.filter(status="new").count()
        confirmed_inquires = query.filter(status="confirmed").count()

        context = {
            "inquiries":inquiries,
            "new_inquires":new_inquires,
            "confirmed_inquires":confirmed_inquires,
        }

        return render(request, "vendor/event_inquiry_page.html", context)

