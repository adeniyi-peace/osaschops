from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, Http404, HttpResponse
from django.views.generic import View, TemplateView
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from  urllib.parse import urlencode
from decimal import Decimal
import hmac
import hashlib
import json
from django.db import transaction


from cart.cart import Cart
from .forms import OrderForm
from shop.models import Order, OrderItem, OrderPack, Product
from .paystack import checkout
from vendor.models import DeliveryZone
from .utils import trigger_order_notification



class CartView(View):
    def get(self, request):
        cart = Cart(request)
        context = {"cart":cart}

        return render(request, "cart/cart_page.html", context)

    def post(self, request):
        cart = Cart(request)
        data = json.loads(request.body.decode())
        item_id = data.get("id")
        quantity = data.get("quantity")
        pack_id = data.get("pack_id") # New: targeted pack

        # Update the specific pack
        cart.add(item_id, quantity, update_quantity=True, pack_id=pack_id)
        
        # We re-render the entire pack or the entire list for simplicity
        # For a high-end feel, re-rendering the pack container is best
        context = {"cart": cart, "total_price": cart.get_total_cost()}
        html = render_to_string("cart/includes/cart_list_partial.html", context, request)
            
        return JsonResponse({
            "html": html, 
            "success": True, 
            "cart": len(cart),
            "total": cart.get_total_cost()
        })

class CartDrawerView(View):
    def get(self, request):
        cart = Cart(request)
        html_drawer = render_to_string("cart/includes/cart_drawer.html", {"cart": cart}, request)

        return JsonResponse({
            "success": True,
            "html_drawer": html_drawer,
            "total": cart.get_total_cost(),
        })
    




class AddToCartView(View):
    def get(self, request, id):
        quantity = request.GET.get("quantity")
        cart = Cart(request)
        if quantity:
            cart.add(id, quantity=int(quantity))
        else:
            cart.add(id,)
        

        return redirect(reverse("cart"))

    def post(self, request):
        cart = Cart(request)
        data = json.loads(request.body.decode())
        item_id = data.get("id")
        quantity = data.get("quantity")
        # Allow specifying a pack_id from frontend, or use the default active one
        pack_id = data.get("pack_id") 

        # Our new cart.add method handles the pack logic
        cart.add(item_id, quantity=int(quantity), update_quantity=True, pack_id=pack_id)

        item = get_object_or_404(Product, id=item_id)

        html_1 = render_to_string(
            "shop/includes/menu_card.html", 
            {"cart":cart, "item":item, "open_status":{"is_open": True}, "reload":True}, 
            request
        )
        html_2 = render_to_string("cart/includes/cart_drawer.html", {"cart":cart}, request)

        return JsonResponse({"success":True, "html_1":html_1, "html_2":html_2, "cart":len(cart)})


class ManagePackView(View):
    def post(self, request):
        cart = Cart(request)
        data = json.loads(request.body)
        action = data.get('action')
        pack_id = data.get('pack_id')
        reload = False

        if action == 'create':
            cart.add_pack()
        elif action == 'duplicate':
            cart.duplicate_pack(pack_id)
        elif action == 'remove':
            if cart.active_pack_id == pack_id:
                reload = True

            cart.remove_pack(pack_id)

        elif action == 'switch':
            cart.set_active_pack(pack_id)
            reload = True

        # Re-render the drawer content
        html_drawer = render_to_string("cart/includes/cart_drawer.html", {"cart": cart}, request)
        
        return JsonResponse({
            "success": True,
            "html_drawer": html_drawer,
            "total": cart.get_total_cost(),
            "cart_count": len(cart),
            "reload":reload,
        })    


class SwitchPackView(View):
    def get(self, request, pack_id):
        cart =Cart(request)
        cart.set_active_pack(pack_id)
        return redirect("cart")


class RemoveFromCartView(View):
    def get(self, request, id):
        cart = Cart(request)
        cart.remove(id)

        return redirect(reverse("cart"))
    



class CheckoutView(View):
    def get(self, request):
        cart = Cart(request)
        form = OrderForm()

        context = {
            "cart":cart,
            "form":form
        }

        return render(request, "cart/checkout_page.html", context)
    

    def post(self, request):
        cart = Cart(request)
        form = OrderForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic(): # Ensures DB integrity
                    order = form.save(commit=False)
                    order.total_amount = cart.get_total_cost() 
                    order.save()

                    for pack in cart:
                        order_pack = OrderPack.objects.create(order=order, name=pack.get("pack_id"))

                        components_to_create = [] 
                        
                        for items in pack.get("items"):
                            product = items["product"]
                            quantities = items["quantity"]
                            price = items['product'].price

                            components_to_create.append(
                                OrderItem(pack=order_pack, product=product, quantity=quantities, price=price)
                            )

                        OrderItem.objects.bulk_create(components_to_create)

                    query_param = {
                        "order_id": order.id
                    }
                    encoded_param = urlencode(query_param)

                    payment_success_url = f"{reverse_lazy('checkout_success')}?{encoded_param}"

                    if order.payment_ref == "Paystack (Card/Transfer)":
                        # http://domain.com/payment-success/2/ 
                        callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

                        order_total = order.total_amount + order.delivery_zone.fee

                        checkout_data = {
                            "email": order.email,
                            "amount": float(order_total) * 100,  # in kobo (₦2500)
                            "currency": "NGN",
                            "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
                            "reference": str(order.id), # generated by developer
                            "callback_url": callback_url,
                            "metadata": {
                                "order_id": str(order.id),
                                # "user_id": request.user.id,
                                # "purchase_id": purchase_id,
                            },
                            "label": f"Checkout For Order No. {order.id}"
                        }
                        
                        status, check_out_session_url_or_error_message = checkout(checkout_data)

                        if status:
                            return redirect(check_out_session_url_or_error_message)
                        else:
                            messages.error(request, check_out_session_url_or_error_message)
                            order.delete()

                    else:
                        # Trigger real time update to vendor pages using websocket
                        trigger_order_notification(order)
                        return redirect(payment_success_url)
                
            except Exception as e:
                messages.error(request, "A system error occurred. Please try again.")
                return redirect("checkout")


        context = {
            "cart":cart,
            "form":form
        }

        return render(request, "cart/checkout_page.html", context)
    

@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhook(View):
    def post(self, request):
        secret = settings.PAYSTACK_SECRET_KEY
        request_body = request.body

        hash = hmac.new(secret.encode("utf-8"), request_body, hashlib.sha512).hexdigest()

        if hash == request.META.get("HTTP_X_PAYSTACK_SIGNATURE"):
            webhook_post_data = json.loads(request_body)

            if webhook_post_data["event"] == "charge.success":
                metadata = webhook_post_data["data"]["metadata"]

                order_id = metadata["order_id"]

                order = get_object_or_404(Order, id=order_id)
                order.paid = True
                order.save()
                # Trigger real time update to vendor pages using websocket
                trigger_order_notification(order)

        return HttpResponse(status=200)



    
class CheckOutSuccessView(View):
    def get(self, request):
        cart = Cart(request)
        cart.clear()
        order_id = request.GET.get("order_id")
        if order_id:
            order = Order.objects.filter(id=order_id).first()
            if order:
                context = {
                    "order":order
                }
                return render(request, "cart/order_success_page.html", context)
        
        return Http404()
    

