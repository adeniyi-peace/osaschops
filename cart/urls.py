from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartView.as_view(), name="cart"),
    path("add-to-cart/<int:id>/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("add-to-cart/", views.AddToCartView.as_view(), name="add_to_cart_post"),

    path("checkout/", views.CheckoutView.as_view(), name="checkout"),

    path("order-success/", views.CheckOutSuccessView.as_view(), name="checkout_success"),
    path("webhook/paystack/", views.PaystackWebhook.as_view()),
]
