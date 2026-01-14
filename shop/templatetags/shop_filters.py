from django import template

register = template.Library()

@register.filter
def get_item(function, key):
    return function.get_item(key).get("quantity")
