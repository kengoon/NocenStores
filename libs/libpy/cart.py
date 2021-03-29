from json import dumps
from functions.list_dict_pos import get_dict_pos
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Cart(Screen):
    app = MDApp.get_running_app()
    p_type = ""

    def go_back(self):
        self.manager.current = self.app.current or "home"
        if self.app.current:
            self.manager.ids.lookout.clear_cache()
            self.manager.ids.lookout.post_data(None, dumps(self.manager.ids.lookout._tmp_data))
        self.app.current = ""

    def transit_to_cartcheckout(self):
        self.manager.prev_screen.append(self.name)
        self.manager.current = "checkout"
        self.manager.ids.checkout.ids.total.right_text = self.ids.total.text
        self.app.data_product = self.ids.rv.data

    def minus_one(self, instance):
        if float(instance.price.translate({ord(i): None for i in "₦,"})) == float(instance.base_price):
            return
        instance.price = \
            f'₦{float(instance.price.translate({ord(i): None for i in "₦,"})) - float(instance.base_price):,}'
        instance.count -= 1
        self.ids.total.text = \
            f"₦{float(self.ids.total.text.translate({ord(i): None for i in '₦,'})) - float(instance.base_price):,}"

    def add_more(self, instance):
        instance.price = \
            f'₦{float(instance.price.translate({ord(i): None for i in "₦,"})) + float(instance.base_price):,}'
        instance.count += 1
        self.ids.total.text = \
            f"₦{float(self.ids.total.text.translate({ord(i): None for i in '₦,'})) + float(instance.base_price):,}"

    def remove_product(self, instance):
        properties = {
            "product": instance.product,
            "source": instance.source,
            "price": instance.price,
            "store": instance.store,
            "count": instance.count,
            "base_price": instance.base_price
        }
        pos = get_dict_pos(self.ids.rv.data, "product", instance.product)
        print(pos)
        self.ids.rv.data[pos] = properties
        self.ids.rv.data.remove(properties)
        self.ids.total.text = \
            f"₦{float(self.ids.total.text.translate({ord(i): None for i in '₦,'})) - float(instance.price.translate({ord(i): None for i in '₦,'})):,}"
