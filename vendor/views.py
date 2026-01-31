from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum, Count, F, ExpressionWrapper, DurationField, Avg, Q
from django.db.models.functions import Now
from django.http import JsonResponse
from django.template.loader import render_to_string
import json
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from shop.models import Order, OrderItem, Product, EventInquiry, Category
from . models import BusinessDay, DeliveryZone, StoreSetting
from . forms import ProductForm, BusinessDayFormSet, DeliveryZoneFormset, StoreSettingForm, VendorLoginForm
from shop.utils import get_current_day_and_time
from . utils import clear_ghost_orders

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Delete orders older than 2 hours that are still 'pending' 
        # and weren't marked as 'Pay on Delivery'
        clear_ghost_orders()
        
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

        
    
class OrderView(LoginRequiredMixin, View):
    def get(self, request):
        # 1. We exclude delivered orders (as you already did)
        # 2. We exclude orders that are Paystack AND unpaid
        active_orders = Order.objects.exclude(
            status="delivered"
        ).exclude(
            Q(payment_ref="Paystack (Card/Transfer)") & Q(paid=False)
        ).prefetch_related(
            'packs__items__product'
        ).select_related('delivery_zone')

        context = {
            "active_orders":active_orders,
        }

        return render(request, "vendor/order_page.html", context)

class OrderReceiptView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.prefetch_related('packs__items__product').select_related('delivery_zone'), 
            id=order_id
        )
        return render(request, "vendor/order_receipt.html", {"order": order})


class UpdateOrderStatusView(LoginRequiredMixin, View):
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


class EODReportView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()
        
        # 1. Get today's completed orders
        # We only count 'delivered' for revenue, but you might want 'ready' too depending on your flow
        today_orders = Order.objects.filter(
            created_at__date=today, 
            status__in=['delivered', 'shipped', 'ready'] 
        )

        # 2. Calculate Financials
        total_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_count = today_orders.count()
        
        # Breakdown by Payment Type (Logic based on your dashboard HTML)
        # We assume if payment_ref is 'Pay on Delivery' it is Cash/POD, otherwise Online
        pod_orders = today_orders.filter(payment_ref='Pay on Delivery')
        online_orders = today_orders.exclude(payment_ref='Pay on Delivery')
        
        cash_revenue = pod_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        online_revenue = online_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # 3. Product Breakdown (Drill down: Order -> Pack -> Item)
        # This tells the kitchen exactly what was consumed today
        items_sold = OrderItem.objects.filter(
            pack__order__in=today_orders
        ).values('product__name').annotate(
            qty=Sum('quantity'),
            total_sales=Sum(F('quantity') * F('price'))
        ).order_by('-qty')

        context = {
            'date': today,
            'total_revenue': total_revenue,
            'total_count': total_count,
            'cash_revenue': cash_revenue,
            'online_revenue': online_revenue,
            'items_sold': items_sold,
            'generated_at': timezone.now(),
        }
        
        return render(request, 'vendor/eod_report_print.html', context)
    

class SalesReportView(LoginRequiredMixin, TemplateView):
    template_name = 'vendor/report_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Date Range Handling (Dynamic)
        start_param = self.request.GET.get('start')
        end_param = self.request.GET.get('end')

        if start_param and end_param:
            start_date = datetime.strptime(start_param, '%Y-%m-%d')
            end_date = datetime.strptime(end_param, '%Y-%m-%d')
            # Make end_date include the full last day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Default to Last 30 Days
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

        # Base Queryset (Filtered by Date)
        orders_queryset = Order.objects.filter(
            status='delivered',
            created_at__range=[start_date, end_date]
        )

        # 2. Key Metrics
        total_revenue = orders_queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = orders_queryset.count()
        avg_order_value = orders_queryset.aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        
        # 3. Event Metrics
        inquiry_query = EventInquiry.objects.filter(created_at__range=[start_date, end_date])
        total_inquiries = inquiry_query.count()
        confirmed_inquiries = inquiry_query.filter(status='confirmed').count()
        conversion_rate = (confirmed_inquiries / total_inquiries * 100) if total_inquiries > 0 else 0

        # 4. CHART DATA: Revenue Trend (Last 7 days within range or selected range)
        # We prepare data for Chart.js (Arrays)
        chart_labels = []
        chart_data = []
        
        # Logic to generate daily breakdown
        delta = end_date - start_date
        days_to_loop = delta.days + 1
        # Cap chart at 14 days to prevent overcrowding, or group by week if longer (simplified here to daily)
        if days_to_loop > 31: days_to_loop = 31 

        for i in range(days_to_loop):
            day = end_date - timedelta(days=i)
            day_revenue = orders_queryset.filter(created_at__date=day.date()).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            chart_labels.insert(0, day.strftime('%d %b')) # e.g. "01 Oct"
            chart_data.insert(0, float(day_revenue))

        # 5. Delivery Zone Performance (Where is the money coming from?)
        zone_performance = orders_queryset.values('delivery_zone__name')\
            .annotate(total=Sum('total_amount'), count=Count('id'))\
            .order_by('-total')

        # 6. Top Selling Products (Drill down: Order -> Pack -> Item)
        # Note: We filter by the pack's order status being delivered
        top_products = OrderItem.objects.filter(
            pack__order__status='delivered',
            pack__order__created_at__range=[start_date, end_date]
        ).values('product__name')\
         .annotate(sold_qty=Sum('quantity'), total_generated=Sum(F('price') * F('quantity')))\
         .order_by('-sold_qty')[:5]

        # 7. Category Data (Kept your logic)
        category_data = Category.objects.annotate(
            sold_count=Count('products__order_items', 
            filter=Q(
                products__order_items__pack__order__paid=True,
                products__order_items__pack__order__created_at__range=[start_date, end_date]
                )
            )
        ).order_by('-sold_count')[:4]

        # 8. Loyal Customers
        loyal_customers = orders_queryset.values('name', 'email') \
            .annotate(order_count=Count('id'), total_spend=Sum('total_amount')) \
            .order_by('-total_spend')[:5]

        context.update({
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'total_inquiries': total_inquiries,
            'conversion_rate': conversion_rate,
            'loyal_customers': loyal_customers,
            'top_products': top_products,
            'zone_performance': zone_performance,
            'category_data': category_data,
            # JSON dumps for Chart.js
            'chart_labels': json.dumps(chart_labels),
            'chart_data': json.dumps(chart_data),
            'start_date': start_date,
            'end_date': end_date,
        })
        return context

class MenuListView(LoginRequiredMixin, View):

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
            
        context = {
            "form":form
        }

        html = render_to_string(
            'vendor/includes/product_form.html', context, request
        )

        return JsonResponse({'success': True, 'html': html})
    
    def post(self, request, pk=None):
        if pk:
            product = get_object_or_404(Product, pk=pk)
            form = ProductForm(request.POST, request.FILES, instance=product)
        else:
            form = ProductForm(request.POST, request.FILES)

            if form.is_valid():
                form.save()

                return redirect("vendor_menu")

        context = {
            "form":form
        }

        html = render_to_string(
            'vendor/includes/product_form.html', context, request
        )

        return JsonResponse({'success': False, 'html': html})
                        

class ProductDeleteView(View):
    """View to return the delete confirmation partial"""
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        html = render_to_string(
            'vendor/includes/delete_confirm.html', {'item': product}, request
        )
        return JsonResponse({'success': True, 'html': html})
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect("vendor_menu")


class SettingsView(LoginRequiredMixin, View):
    def get(self, request):
        business_day = BusinessDay.objects.all()
        delivery_zone = DeliveryZone.objects.all()
        store_settings = get_object_or_404(StoreSetting, name="Osaschops")
        business_formset = BusinessDayFormSet(queryset=business_day)
        delivery_formset = DeliveryZoneFormset(queryset=delivery_zone, prefix="delivery_zone")
        store_form = StoreSettingForm(instance=store_settings)

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

            return redirect("store_profile")

        context = {
            "business_formset":business_formset,
            "delivery_formset":delivery_formset,
            "store_form":store_form,
            "store_settings":store_settings,
        }

        return render(request, "vendor/settings_page.html", context)
        

class EventInquiryView(LoginRequiredMixin, View):
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

    def post(self, request):
        inquiry_id = request.POST.get('inquiry_id')
        new_status = request.POST.get('status')
        inquiry = get_object_or_404(EventInquiry, id=inquiry_id)
        
        if new_status in ["contacted", "confirmed", "cancelled"]:
            inquiry.status = new_status
            inquiry.save()
            messages.success(request, f"Inquiry for {inquiry.name} updated to {new_status}!")
        
        return redirect("vendor_event_inquiry")



class StoreProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile = StoreSetting.objects.first() # Assuming one vendor for now
        day, time = get_current_day_and_time()
        business_day = get_object_or_404(BusinessDay, day=day)
        context = {'profile': profile, "business_day":business_day}
        return render(request, "vendor/store_profile.html", context)

    def post(self, request):
        day, time = get_current_day_and_time()
        business_day = get_object_or_404(BusinessDay, day=day)
        # Toggle Store Status (Open/Closed) via AJAX or Form
        if 'toggle_status' in request.POST:
            business_day.is_open = not business_day.is_open
            business_day.save()
            return JsonResponse({'status': 'success', 'is_open': business_day.is_open})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("vendor_dashboard")

        form = VendorLoginForm(request)

        return render(request, "vendor/login_page.html", {
            "form": form
        })

    def post(self, request):

        form = VendorLoginForm(request, data=request.POST )

        
        if form.is_valid():
            user = form.get_user()

            if not user.is_staff:
                messages.error(request, "Access denied.")
                return redirect("vendor_login")

            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid login details")

        return render(request, "vendor/login_page.html", {
            "form": form
        })


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("vendor_login")
