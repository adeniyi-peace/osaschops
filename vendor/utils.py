'''from twilio.rest import Client
from django.conf import settings
from shop.templatetags.shop_filters import shop

def send_whatsapp_update(order):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Format the Pack Summary
    pack_summary = ""
    for pack in order.packs.all():
        pack_summary += f"\n📦 *{pack.name}*:"
        for item in pack.items.all():
            pack_summary += f"\n  - {item.quantity}x {item.product.name}"
    
    message_body = (
        f"Hello {order.name}! 🌶️\n\n"
        f"Your *Osaschops* order *#{order.id}* is now out for delivery! 🛵\n"
        f"--------------------------"
        f"{pack_summary}\n"
        f"--------------------------\n"
        f"💰 *Total:* ₦{order.total_amount + 2500}\n"
        f"📍 *Address:* {order.address}\n\n"
        f"Get your plates ready, the levels are coming! 🔥"
    )

    try:
        message = client.messages.create(
            from_='whatsapp:' + shop.whatsapp_number,
            body=message_body,
            to='whatsapp:' + order.phone # Ensure phone includes country code like +234
        )
        return True
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False'''