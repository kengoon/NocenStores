from json import dumps, loads
from classes.notification import notify
from kivy.network.urlrequest import UrlRequest
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from plyer import call


class ProductLookOut(Screen):
    url = "https://nocenstore.pythonanywhere.com/"
    tmp_data = None
    _tmp_data = None
    selected_size = ""
    app = MDApp.get_running_app()
    p_type = ""

    def go_back(self):
        self.manager.current = "category"

    @staticmethod
    def call_customer_care():
        call.makecall("08129330697")

    def enter_cart(self):
        self.app.current = self.name
        self.manager.prev_screen.append(self.name)
        self.manager.current = "cart"

    def on_leave(self, *args):
        if not self.app.current:
            self.clear_cache()

    def update_interface(self, data):
        self.tmp_data = data
        new_data = data.copy()
        if self.app.login:
            new_data.update({"userId": self.app.firebase["userId"]})
        UrlRequest(
            url=f"{self.url}showcaseProduct",
            req_body=dumps(new_data),
            on_error=self.network_error,
            on_success=self.post_data
        )

    def network_error(self, *args):
        notify("You lost connection, check your Internet settings")
        self.update_interface(self.tmp_data)

    def post_data(self, instance, data):
        new_data = loads(data)
        self._tmp_data = new_data.copy()
        self.ids.product_price.text = f"₦{float(new_data['price']) + 5/100 * float(new_data['price']):,}"
        self.ids.description.text = new_data["description"].split("size(")[0]
        for i in range(1, 4):
            self.ids[f"image{i}"].source = new_data[str(i)]

        if "size" in new_data["description"]:
            size_list = new_data["description"].split("(")[1].split(")")[0]

            for i in loads(size_list):
                self.ids.rvs.data.append({"text_item": str(i)})
        self.ids.buttons.disabled = False
        self.ids.buttons.opacity = 1
        if "saved" in new_data and new_data["saved"]:
            self.ids.save.icon = "heart"
        if "FairlyUsed" == new_data["type"]:
            self.ids.save.disabled = True
            self.p_type = new_data["type"]
        else:
            self.ids.save.disabled = False
            self.p_type = ""

    def change_circle(self):
        for i in range(1, 4):
            if self.ids.mg.current == str(i):
                self.ids[f"ico{i}"].icon = "circle"
                continue
            self.ids[f"ico{i}"].icon = "circle-outline"

    def clear_cache(self):
        for i in range(1, 4):
            self.ids[f"image{i}"].source = ""
        self.ids.product_price.text = ""
        self.ids.description.text = ""
        self.ids.rvs.data = []
        self.ids.holder.clear_widgets()

    def save_unsave(self, instance):
        if not self.app.login:
            notify("please login to continue")
            self.app.current = self.name
            self.manager.current = "login"
            return
        instance.icon = "heart" if "outline" in instance.icon else "heart-outline"
        instance.disabled = True

        def process(instance_object, data):
            notify(data)
            instance.disabled = False
            if self.manager.ids.saved.enter:
                self.manager.ids.saved.ids.rv.data.append(
                    {
                        "imagePath": self.ids.image1.source,
                        "price": self.ids.product_price.text.replace("₦", ""),
                        "product": self.ids.product_name.text,
                        "store": self.ids.store.text
                    }
                )

        def network_error(*args):
            notify("network error, please subscribe")
            instance.disabled = False
            instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        def server_error(*args):
            notify("server is down, fixing...")
            instance.disabled = False
            instance.icon = "heart" if "outline" in instance.icon else "heart-outline"

        data = {
            self.ids.product_name.text: {
                "imagePath": self.ids.image1.source,
                "price": self.ids.product_price.text.replace("₦", ""),
                "product": self.ids.product_name.text,
                "store": self.ids.store.text,
            },
            "type": instance.icon,
            "userId": self.app.firebase["userId"],
            "idToken": self.app.firebase["idToken"]
        }
        UrlRequest(
            url=self.url + "saveMyProduct",
            req_body=dumps(data),
            on_success=process,
            on_error=network_error,
            on_failure=server_error
        )

    def add_to_cart(self):
        if not self.app.login:
            notify("please login to continue")
            self.app.current = self.name
            self.manager.current = "login"
            return
        cart = {
            "product": self.ids.product_name.text,
            "source": self.ids.image1.source,
            "price": self.ids.product_price.text,
            "store": self.ids.store.text,
            "count": 1,
            "base_price": self.ids.product_price.text.translate({ord(i): None for i in "₦,"})
        }
        a = list(filter(lambda product: self.ids.product_name.text == product["product"],
                        self.manager.ids.cart.ids.rv.data))
        if a:
            if self.p_type == "FairlyUsed":
                self.manager.current = "cart"
                return
            cart.update({"p_type": False})
            cart["count"] = a[0]["count"]
            top_up = f'₦{float(a[0]["price"].translate({ord(i): None for i in "₦,"})) + float(cart["price"].translate({ord(i): None for i in "₦,"})):,}'
            cart["price"] = a[0]["price"]
            index = self.manager.ids.cart.ids.rv.data.index(cart)
            cart["count"] += 1
            cart["price"] = top_up
            self.manager.ids.cart.ids.rv.data[index] = cart
            notify(f"{self.ids.product_name.text} = {self.manager.ids.cart.ids.rv.data[index]['count']} product")
        else:
            if self.p_type == "FairlyUsed":
                cart.update({"p_type": True})
            else:
                cart.update({"p_type": False})
            self.manager.ids.cart.ids.rv.data.append(cart)
            notify(f"{self.ids.product_name.text} = 1 product")
            if self.p_type == "FairlyUsed":
                self.manager.current = "cart"
                cart_data = self.manager.ids.cart.ids.rv.data
                cart_total = sum(
                    float(cart_data[i]["price"].translate({ord(i): None for i in "₦,"})) for
                    i, _ in enumerate(cart_data)
                )
                self.manager.ids.cart.ids.total.text = f"₦{cart_total:,}"
                return
        self.ids.save.dispatch("on_release") if self.ids.save.icon == "heart-outline" else None
        cart_data = self.manager.ids.cart.ids.rv.data
        cart_total = sum(
            float(cart_data[i]["price"].translate({ord(i): None for i in "₦,"})) for
            i, _ in enumerate(cart_data)
        )
        self.manager.ids.cart.ids.total.text = f"₦{cart_total:,}"

