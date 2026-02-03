from django.shortcuts import render
from django.views.generic import View, FormView, TemplateView
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
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
        products =Product.objects.all().annotate(best_sellers=Count("order_items")).order_by("best_sellers")[:6]

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

class HealthView(View):
    def get(self, request):
        return  HttpResponse("OK")
