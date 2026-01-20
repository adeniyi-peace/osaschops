from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from shop.models import Order
from django.template.loader import render_to_string

def trigger_order_notification(order):
    """
    Renders the order card and pushes it to the vendor via WebSockets.
    """
    # 1. Render the HTML snippet
    html = render_to_string("vendor/includes/order_card.html", {"order": order})

    # 2. Prepare the data
    delivery_fee = order.delivery_zone.fee if order.delivery_zone else 0
    grand_total = order.total_amount + delivery_fee

    # 3. Send to Channels
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "vendor_orders",
        {
            "type": "order_alert",
            "message": "New Order Received!",
            "data": {
                "id": order.id,
                "name": order.name, 
                "total": f"{grand_total:,}",
                "html": html
            }
        }
    )