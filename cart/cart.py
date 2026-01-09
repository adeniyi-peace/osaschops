from django.conf import settings

from shop.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    
    def __iter__(self):
        for p_id_str, item_data in self.cart.items():
            p_id = int(p_id_str)
            product = Product.objects.get(pk=p_id)

            item = item_data.copy()
            item["product"] = product
            item["total_price"] = int(product.price) * int(item["quantity"])

            yield item


    def __len__(self):
        return sum(int(item["quantity"] )for item in self.cart.values())
    

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True


    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        if product_id not in self.cart:
            self.cart[product_id] = {"quantity":quantity, "id":product_id}

        if update_quantity:
            self.cart[product_id]["quantity"] = int(quantity)

            if self.cart[product_id]["quantity"] == 0:
                self.remove(product_id)

        self.save()


    def remove(self, product_id):
        # If you are encountering errors such as keyerror or product not deleting,
        # it is going to be due to product_id not being a string. To rectify the error
        # change product_id to string 
        if product_id in self.cart:
            del self.cart[product_id]

            self.save()


    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total_cost(self):
        product_ids = self.cart.keys()
        # Fetch all products in the cart in ONE query
        products = Product.objects.filter(id__in=product_ids)
        
        total = 0
        for product in products:
            quantity = self.cart[str(product.id)]['quantity']
            total += product.price * quantity
        return total
    
    def get_item(self, product_id):
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]
        
        else:
            return None