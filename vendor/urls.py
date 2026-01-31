from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("orders/", views.OrderView.as_view(), name="orders"),
    path("orders/order-receipt/<order_id>", views.OrderReceiptView.as_view(), name="order_receipt"),
    path("orders/<int:order_id>/update-status/", views.UpdateOrderStatusView.as_view(), name="order_status_update"),
    path('report/eod/', views.EODReportView.as_view(), name='eod_report'),
    path("sales-report/", views.SalesReportView.as_view(), name="sales_report"),
    path("menu/", views.MenuListView.as_view(), name="vendor_menu"),
    path("menu/add-menu/", views.AddEditProductView.as_view(), name="add_menu"),
    path("menu/edit-menu/<int:pk>/", views.AddEditProductView.as_view(), name="edit_menu"),
    path("menu/delete-menu/<int:pk>/", views.ProductDeleteView.as_view(), name="delete_menu"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("event-inquiry/", views.EventInquiryView.as_view(), name="vendor_event_inquiry"),
    path("store-profile/", views.StoreProfileView.as_view(), name="store_profile"),

    path("login/", views.LoginView.as_view(), name="vendor_login"),
    path("logout/", views.LogoutView.as_view(), name="vendor_logout"),
    
]
