from django.conf import settings

from shop.models import Product


class Cart(object):
    """
    Cart structure 

    cart = {
        "pack_1": {
            "name": "Office Party Pack",
            "items": {
                "prod_id_1": {"quantity": 10},
                "prod_id_2": {"quantity": 5}
            }
        },
        "pack_2": {
            "name": "Home Treats",
            "items": {
                "prod_id_1": {"quantity": 20}
            }
        }
    }

    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # Initialize with one default pack
            cart = self.session[settings.CART_SESSION_ID] = {
                "pack_1": {"name": "Pack 1", "items": {}}
            }
        self.cart = cart
        
        # Track which pack the user is currently editing
        active_pack_id = self.session.get('active_pack_id')
        if not active_pack_id:
            active_pack_id = self.session["active_pack_id"] = "pack_1"

        self.active_pack_id = active_pack_id

    
    def __iter__(self):
        """Iterate through packs and their resolved products"""
        product_ids = []
        for pack in self.cart.values():
            product_ids.extend(pack['items'].keys())
        
        products = Product.objects.filter(id__in=product_ids)
        product_dict = {str(p.id): p for p in products}

        for pack_id, pack_data in self.cart.items():
            pack_items = []
            pack_total = 0
            
            for p_id, item_data in pack_data['items'].items():
                product = product_dict.get(p_id)
                if product:
                    total_item_price = product.price * item_data['quantity']
                    pack_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'total_price': total_item_price
                    })
                    pack_total += total_item_price
            
            yield {
                'pack_id': pack_id,
                'name': pack_data['name'],
                'items': pack_items,
                'total_price': pack_total,
                'is_active': pack_id == self.active_pack_id
            }


    def __len__(self):
        quantities = []
        for pack in self.cart.values():
            for item in pack['items'].values():
                quantities.append(int(item['quantity']))
        return sum(quantities)

    
    def set_active_pack(self, pack_id):
        if pack_id in self.cart:
            self.active_pack_id = pack_id
            self.session['active_pack_id'] = pack_id
            self.session.modified = True
    
    def get_active_pack(self, pack_id):
        if pack_id in self.cart:
            return self.session['active_pack_id'] 

    def add_pack(self, name=None):
        new_id = f"pack_{len(self.cart) + 1}"
        self.cart[new_id] = {
            "name": name or f"Pack {len(self.cart) + 1}",
            "items": {}
        }
        self.save()
        return new_id


    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
    


    def add(self, product_id, quantity=1, update_quantity=False, pack_id=None):
        # Use provided pack_id or fall back to the active one
        target_pack = pack_id or self.active_pack_id
        product_id = str(product_id)
        
        items = self.cart[target_pack]["items"]

        if product_id not in items:
            items[product_id] = {"quantity": 0}

        if update_quantity:
            items[product_id]["quantity"] = int(quantity)
        else:
            items[product_id]["quantity"] += int(quantity)

        if items[product_id]["quantity"] <= 0:
            del items[product_id]

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
        del self.session["active_pack_id"]
        self.session.modified = True

    def get_total_cost(self):
        all_product_ids = set()
        for pack in self.cart.values():
            all_product_ids.update(pack['items'].keys())

        products = Product.objects.filter(id__in=all_product_ids)
        
        # 3. Create a mapping of {id_string: price} for fast lookup
        price_map = {str(p.id): p.price for p in products}

        # 4. Calculate total using the map (No more DB hits)
        total = 0
        for pack in self.cart.values():
            for p_id, item in pack['items'].items():
                price = price_map.get(str(p_id), 0)
                total += price * item['quantity']
                
        return total

    
    def get_item(self, product_id):
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]
        
        else:
            return 
            
    def items(self):
        return self.cart

    def duplicate_pack(self, pack_id):
        if pack_id in self.cart:
            new_id = f"pack_{len(self.cart) + 1}"
            # Deep copy the pack data
            new_pack = {
                "name": f"{self.cart[pack_id]['name']} (Copy)",
                "items": self.cart[pack_id]['items'].copy()
            }
            self.cart[new_id] = new_pack
            self.save()
            return new_id

    def remove_pack(self, pack_id):
        if pack_id in self.cart and len(self.cart) > 1:
            del self.cart[pack_id]
            # If we deleted the active pack, set active to the first available one
            if self.active_pack_id == pack_id:
                first_pack_in_cart = list(self.cart.keys())[0]
                self.set_active_pack(first_pack_in_cart )
            self.save()