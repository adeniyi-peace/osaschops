from django.shortcuts import render
from django.views.generic import View
from django.db import Count

from vendor.models import StoreSetting
from . models import Category, Product


class HomePageView(View):
    def get(self, request):
        store = StoreSetting.objects.get(name="Osaschops")
        categories = Category.objects.all().count()
        products =Product.objects.all().annotate(best_sellers=Count("order_items")).order_by("best_sellers")

        context ={
            "store":store,
            "categories":categories,
            "products":products,
        }
        return render(request, "shop/home_page.html", context)
