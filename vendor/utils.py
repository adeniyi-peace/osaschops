import os
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import logging
from shop.models import Order
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
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

logger = logging.getLogger(__name__)

def validate_audio_duration(file):
    """Ensures audio files are not longer than 10 seconds."""
    try:
        # Temporary check for extension
        ext = os.path.splitext(file.name)[1].lower()
        audio = None
        
        if ext == '.mp3':
            audio = MP3(file)
        elif ext == '.wav':
            audio = WAVE(file)
        
        if audio:
            if audio.info.length > 10:
                raise ValidationError(f"Audio is too long ({round(audio.info.length, 1)}s). Max 10s allowed.")
        else:
            raise ValidationError("Unsupported audio format. Please upload an MP3 or WAV.")

    except ValidationError:
        # Re-raise validation errors so they reach the user
        raise 
    except Exception as e:
        # Log the actual error for the developer
        logger.error(f"Audio validation failed: {str(e)}")
        # Tell the user the file is unreadable/corrupted
        raise ValidationError("Could not verify audio duration. The file might be corrupted or in an invalid format.")

def clear_ghost_orders():
    # Delete orders older than 2 hours that are still 'pending' 
    # and weren't marked as 'Pay on Delivery'
    expiry_time = timezone.now() - timedelta(hours=2)
    Order.objects.filter(
        status='pending', 
        created_at__lt=expiry_time,
        payment_ref="Paystack (Card/Transfer)"
    ).delete()