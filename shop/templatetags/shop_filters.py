from django import template
from vendor.models import BusinessDay
from django.core.cache import cache

from ..utils import is_store_currently_open
from vendor.models import StoreSetting


register = template.Library()

SHOP = "vendor_unread_message_count"
CACHE_TIMEOUT = 60 * 5

@register.filter
def get_pack_qty(cart, item_id):
    """Usage: {{ cart|get_pack_qty:item.id }}"""
    # Find the active pack in the cart session
    active_id = cart.active_pack_id
    pack_items = cart.cart.get(active_id, {}).get('items', {})
    return pack_items.get(str(item_id), {}).get('quantity', 0)



@register.simple_tag()
def business_open():
    status, message = is_store_currently_open(BusinessDay.objects.all())
    return {
        'is_open': status,
        'message': message
    }


@register.simple_tag(takes_context=True)
def shop(context):
    shop = cache.get(SHOP)

    if shop == None:
        try:
            shop = StoreSetting.objects.first()
        except AttributeError:
            shop = 0
        
        cache.set(SHOP, shop, CACHE_TIMEOUT)

    return shop
