from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name="homepage"),
    path("menu/", views.MenuView.as_view(), name="menu"),
    path("bulk-order/", views.BulkOrderView.as_view(), name="bulk_order"),
]