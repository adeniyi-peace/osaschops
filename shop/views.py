from django.shortcuts import render
from django.views.generic import View, FormView, TemplateView
from django.db.models import Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib import messages

from vendor.models import StoreSetting
from . models import Category, Product
from cart.cart import Cart
from .forms import BulkOrderForm

class HomePageView(View):
    def get(self, request):
        store = StoreSetting.objects.get(name="Osaschops")
        categories = Category.objects.all()
        products =Product.objects.all().annotate(best_sellers=Count("order_items")).order_by("best_sellers")

        context ={
            "store":store,
            "categories":categories,
            "products":products,
        }
        return render(request, "shop/home_page.html", context)
    
class MenuView(View):
    def get(self, request):
        category = request.GET.get("category")

        products = Product.objects.all()

        if category:
            products = products.filter(category__slug=category)

        categories = Category.objects.all()

        context = {
            "categories":categories,
            "products":products,
        }

        return render(request, "shop/menu.html", context)
    
    def post(self, request):
        """AJAX add-to-cart and re-render product list WITH ACTIVE FILTERS & PAGINATION"""
        cart = Cart(request)

        category = request.GET.get("category")

        products = Product.objects.all()

        if category:
            products = products.filter(category__slug=category)

        product_id = request.POST.get("product_id")
        cart.add_product(product_id=product_id)

        html = render_to_string(
            "shop/includes/menu_card.html",
            {
                "products": products,
                "cart": cart,
                "filters": request.GET,
                # Ensures opens status is not false
                "open_status":{"is_open":True}
            },
            request=request
        )

        return JsonResponse({"html": html, "status": True, "cart":len(cart)})
    
class BulkOrderView(FormView):
    form_class = BulkOrderForm
    template_name ="shop/bulk_order_page.html"
    success_url = reverse_lazy("homepage")

    def form_valid(self, form):
        # set django message
        messages.success(self.request, "Your bulk order request has been submitted succesfully. We will contact you via WhatsApp or Phone within 24 hours.")
        form.save()
        return super().form_valid(form)

class AboutUsPage(TemplateView):
    template_name="shop/about_us_page.html"
