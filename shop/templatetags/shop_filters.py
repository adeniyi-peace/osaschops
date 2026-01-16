from django import template

register = template.Library()

@register.filter
def get_pack_qty(cart, item_id):
    """Usage: {{ cart|get_pack_qty:item.id }}"""
    # Find the active pack in the cart session
    active_id = cart.active_pack_id
    pack_items = cart.cart.get(active_id, {}).get('items', {})
    return pack_items.get(str(item_id), {}).get('quantity', 0)
